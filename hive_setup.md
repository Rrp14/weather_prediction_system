1) install hive 

2)in terminal type hive

than:-

CREATE EXTERNAL TABLE climate_predictions (
    sensor_id_hash STRING,
    timestamp STRING,
    temperature DOUBLE,
    humidity DOUBLE,
    wind_speed DOUBLE,
    alert STRING,
    predicted_event STRING,
    risk_level STRING,
    confidence DOUBLE
)
STORED AS PARQUET
LOCATION '/climate-predictions';

3) verify table SELECT * FROM climate_predictions LIMIT 10;

4) start hiveserver2 
hiveserver2 &

5) install
pip install pyhive thrift thrift-sasl sasl


*) we are running hive in binary mode u can use http mode supported by latest version 

open hive-site.xml
nano $HIVE_HOME/conf/hive-site.xml

<?xml version="1.0" encoding="UTF-8"?>
<configuration>

  <!-- MySQL Metastore -->
  <property>
    <name>javax.jdo.option.ConnectionURL</name>
    <value>jdbc:mysql://localhost/metastore?createDatabaseIfNotExist=true</value>
  </property>

  <property>
    <name>javax.jdo.option.ConnectionDriverName</name>
    <value>com.mysql.cj.jdbc.Driver</value>
  </property>

  <property>
    <name>javax.jdo.option.ConnectionUserName</name>
    <value>hiveuser</value>
  </property>

  <property>
    <name>javax.jdo.option.ConnectionPassword</name>
    <value>hivepassword</value>
  </property>

  <property>
    <name>datanucleus.autoCreateSchema</name>
    <value>true</value>
  </property>

  <property>
    <name>hive.server2.enable.doAs</name>
    <value>false</value>
  </property>

  <!-- ADD THESE -->
  <property>
    <name>hive.server2.transport.mode</name>
    <value>binary</value>
  </property>

  <property>
    <name>hive.server2.thrift.port</name>
    <value>10000</value>
  </property>

  <property>
    <name>hive.server2.authentication</name>
    <value>NOSASL</value>
  </property>

</configuration>
