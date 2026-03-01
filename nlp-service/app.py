from fastapi import FastAPI
from transformers import pipeline
import torch

torch.set_grad_enabled(False)

app = FastAPI()

classifier = pipeline(
    "zero-shot-classification",
    model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli",
    device=0,
    torch_dtype=torch.float16
)
classifier.model.eval()

candidate_labels = [
    "heatwave",
    "cyclone",
    "flood",
    "storm",
    "normal weather"
]

@app.post("/analyze_batch")
def analyze_batch(data: dict):
    alerts = data.get("alerts", [])

    if not alerts:
        return {"results": []}

    results = classifier(
        alerts,
        candidate_labels,
        truncation=True
    )

    output = []

    for alert, result in zip(alerts, results):
        top_label = result["labels"][0]
        confidence = result["scores"][0]

        risk_level = "LOW"
        if top_label in ["cyclone", "flood", "storm"]:
            risk_level = "HIGH"
        elif top_label == "heatwave":
            risk_level = "MEDIUM"

        output.append({
            "alert": alert,
            "predicted_event": top_label,
            "risk_level": risk_level,
            "confidence": round(confidence, 3)
        })

    return {"results": output}