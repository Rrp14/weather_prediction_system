from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

spark = SparkSession.builder \
    .appName("ClimateStreaming") \
    .config("spark.sql.shuffle.partitions", "8") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# =========================
# SCHEMA
# =========================

schema = StructType([
    StructField("sensor_id", StringType()),
    StructField("timestamp", StringType()),
    StructField("location", StructType([
        StructField("lat", DoubleType()),
        StructField("lon", DoubleType())
    ])),
    StructField("temperature", DoubleType()),
    StructField("humidity", DoubleType()),
    StructField("wind_speed", DoubleType()),
    StructField("alert", StringType())
])

# =========================
# READ FROM KAFKA
# =========================

df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "climate-data") \
    .option("startingOffsets", "latest") \
    .load()

json_df = df.selectExpr("CAST(value AS STRING)")

parsed_df = json_df.select(
    from_json(col("value"), schema).alias("data")
).select("data.*")

parsed_df = parsed_df.withColumn(
    "event_time",
    to_timestamp(col("timestamp"))
)

# =========================
# GDPR ANONYMIZATION
# =========================

parsed_df = parsed_df.withColumn(
    "sensor_id_hash",
    sha2(col("sensor_id"), 256)
).drop("sensor_id")

# =========================
# 1️⃣ WINDOW AGGREGATION
# =========================

watermarked = parsed_df.withWatermark("event_time", "2 minutes")

windowed = watermarked.groupBy(
    window(col("event_time"), "5 minutes"),
    col("sensor_id_hash")
).agg(
    avg("temperature").alias("avg_temp"),
    avg("humidity").alias("avg_humidity"),
    max("wind_speed").alias("max_wind_speed")
)

agg_query = windowed.writeStream \
    .outputMode("append") \
    .format("parquet") \
    .option("path", "hdfs://localhost:9000/climate-aggregates") \
    .option("checkpointLocation", "hdfs://localhost:9000/climate-aggregates-checkpoint") \
    .start()

# =========================
# 2️⃣ SEND ALERTS TO KAFKA
# =========================

alerts_df = parsed_df.filter(col("alert").isNotNull())

alerts_kafka_df = alerts_df.select(
    to_json(struct("*")).alias("value")
)

alerts_query = alerts_kafka_df.writeStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("topic", "alerts-raw") \
    .option("checkpointLocation", "hdfs://localhost:9000/alerts-raw-checkpoint") \
    .outputMode("append") \
    .start()

# =========================
# 3️⃣ READ ENRICHED ALERTS
# =========================

enriched_schema = StructType([
    StructField("sensor_id_hash", StringType()),
    StructField("timestamp", StringType()),
    StructField("temperature", DoubleType()),
    StructField("humidity", DoubleType()),
    StructField("wind_speed", DoubleType()),
    StructField("alert", StringType()),
    StructField("predicted_event", StringType()),
    StructField("risk_level", StringType()),
    StructField("confidence", DoubleType())
])

enriched_stream = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "alerts-enriched") \
    .option("startingOffsets", "latest") \
    .load()

enriched_json = enriched_stream.selectExpr("CAST(value AS STRING)")

final_df = enriched_json.select(
    from_json(col("value"), enriched_schema).alias("data")
).select("data.*")

final_query = final_df.writeStream \
    .format("parquet") \
    .option("path", "hdfs://localhost:9000/climate-predictions") \
    .option("checkpointLocation", "hdfs://localhost:9000/climate-predictions-checkpoint") \
    .outputMode("append") \
    .start()

spark.streams.awaitAnyTermination()