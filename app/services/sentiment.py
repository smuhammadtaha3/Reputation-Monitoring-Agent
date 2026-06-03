from transformers import pipeline

_classifier = None

def get_classifier():
    global _classifier
    if _classifier is None:
        _classifier = pipeline(
            task="sentiment-analysis",
            model="cardiffnlp/twitter-roberta-base-sentiment-latest",
            device=-1
        )
    return _classifier

def analyze(text: str) -> dict:
    clf = get_classifier()
    result = clf(text[:512])[0]
    label = result["label"].lower()
    return {
        "label": label,
        "score": round(result["score"], 4),
        "is_negative": label == "negative"
    }