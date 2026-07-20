from transformers import pipeline
import os

_classifier = None

# Pehle local fine-tuned model dhundo, warna original use karo
MODEL_PATH = os.path.join(
    os.path.dirname(__file__), '../../models/fine_tuned_model'
)
MODEL_NAME = MODEL_PATH if os.path.exists(MODEL_PATH) \
             else "cardiffnlp/twitter-roberta-base-sentiment-latest"

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
            device=-1
        )
    return _classifier

def analyze(text: str) -> dict:
    clf    = get_classifier()
    result = clf(text[:512])[0]
    label  = LABEL_MAP.get(result["label"].lower(), result["label"].lower())
    return {
        "label":       label,
        "score":       round(result["score"], 4),
        "is_negative": label == "negative"
    }