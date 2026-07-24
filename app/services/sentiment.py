import os
import requests

HF_TOKEN = os.environ.get("HF_TOKEN")
MODEL_NAME = os.environ.get("MODEL_NAME", "TAHA4/reputation-sentiment-model")
API_URL = f"https://api-inference.huggingface.co/models/{MODEL_NAME}"

LABEL_MAP = {
    "label_0": "negative",
    "label_1": "neutral",
    "label_2": "positive",
    "negative": "negative",
    "neutral":  "neutral",
    "positive": "positive"
}

def analyze(text: str) -> dict:
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    response = requests.post(API_URL, headers=headers, json={"inputs": text[:512]})
    result = response.json()[0][0]
    label = LABEL_MAP.get(result["label"].lower(), result["label"].lower())
    return {
        "label": label,
        "score": round(result["score"], 4),
        "is_negative": label == "negative"
    }