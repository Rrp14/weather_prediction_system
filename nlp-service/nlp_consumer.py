from kafka import KafkaConsumer, KafkaProducer
import json
from transformers import pipeline
import torch

# Load GPU model
classifier = pipeline(
    "zero-shot-classification",
    model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli",
    device=0,
    torch_dtype=torch.float16
)

candidate_labels = [
    "heatwave",
    "cyclone",
    "flood",
    "storm",
    "normal weather"
]

consumer = KafkaConsumer(
    "alerts-raw",
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    auto_offset_reset="latest",
    group_id="nlp-group"
)

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

print("🚀 NLP Kafka consumer started...")

batch = []

for message in consumer:
    batch.append(message.value)

    if len(batch) >= 32:  # GPU batch size
        alerts = [item["alert"] for item in batch]

        results = classifier(alerts, candidate_labels)

        for data, result in zip(batch, results):
            predicted = result["labels"][0]
            confidence = result["scores"][0]

            risk_level = "LOW"
            if predicted in ["cyclone", "flood", "storm"]:
                risk_level = "HIGH"
            elif predicted == "heatwave":
                risk_level = "MEDIUM"

            enriched = {
                **data,
                "predicted_event": predicted,
                "risk_level": risk_level,
                "confidence": round(confidence, 3)
            }

            producer.send("alerts-enriched", enriched)

        batch = []