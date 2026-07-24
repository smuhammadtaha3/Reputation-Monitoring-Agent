from transformers import pipeline
import os
import torch

_classifier = None
MODEL_NAME = os.environ.get("MODEL_NAME", "TAHA4/reputation-sentiment-model")

LABEL_MAP = {
    "label_0": "negative",
    "label_1": "neutral",
    "label_2": "positive",
    "negative": "negative",
    "neutral":  "neutral",
    "positive": "positive"
}

def get_classifier():
    global _classifier
    if _classifier is None:
        print(f"Loading model from: {MODEL_NAME}")
        _classifier = pipeline(
            task="sentiment-analysis",
            model=MODEL_NAME,
            device=-1,
            torch_dtype= torch.float32,
            model_kwargs={"low_cpu_mem_usage": True}
        )  # type: ignore
    return _classifier

def analyze(text: str) -> dict:
    clf    = get_classifier()
    result = clf(text[:512])[0]  # type: ignore
    label  = LABEL_MAP.get(result["label"].lower(), result["label"].lower())  # type: ignore
    return {
        "label":       label,
        "score":       round(result["score"], 4),  # type: ignore
        "is_negative": label == "negative"
    }