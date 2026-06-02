from transformers import pipeline

# Loaded once when Python imports this module
_classifier = pipeline(
    task="sentiment-analysis",
    model="cardiffnlp/twitter-roberta-base-sentiment-latest"
)

NEGATIVE_LABELS = {"negative", "LABEL_0"}

def analyze(text: str) -> dict:
    """Returns {'label': 'negative', 'score': 0.97}"""
    result = _classifier(text[:512])[0]  # truncate long reviews
    return {
        "label": result["label"].lower(),
        "score": round(result["score"], 4),
        "is_negative": result["label"].lower() in NEGATIVE_LABELS
    }