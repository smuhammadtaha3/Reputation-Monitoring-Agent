import json
import torch
import numpy as np
from torch.utils.data import Dataset, DataLoader
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer
)
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# ── 1. Load data ──
with open('../data/training_reviews.json') as f:
    data = json.load(f)

texts  = [d['text']  for d in data]
labels = [d['label'] for d in data]

train_texts, val_texts, train_labels, val_labels = train_test_split(
    texts, labels, test_size=0.2, random_state=42, stratify=labels
)

print(f"Train: {len(train_texts)} | Val: {len(val_texts)}")

# ── 2. Tokenizer ──
MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"
tokenizer  = AutoTokenizer.from_pretrained(MODEL_NAME)

# ── 3. Dataset class ──
class ReviewDataset(Dataset):
    def __init__(self, texts, labels):
        self.encodings = tokenizer(
            texts,
            truncation=True,
            padding=True,
            max_length=512,
            return_tensors='pt'
        )
        self.labels = labels

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        item = {k: v[idx] for k, v in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx], dtype=torch.long)
        return item

train_dataset = ReviewDataset(train_texts, train_labels)
val_dataset   = ReviewDataset(val_texts,   val_labels)

# ── 4. Load model ──
model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME,
    num_labels=3,
    ignore_mismatched_sizes=True
)

# ── 5. Metrics function ──
def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    return {'accuracy': accuracy_score(labels, preds)}

# ── 6. Training arguments ──
training_args = TrainingArguments(
    output_dir='../models/fine_tuned_model',
    num_train_epochs=3,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    warmup_steps=10,
    weight_decay=0.01,
    evaluation_strategy='epoch',
    save_strategy='epoch',
    load_best_model_at_end=True,
    logging_dir='../models/logs',
    logging_steps=10,
    report_to='none'
)

# ── 7. Trainer ──
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    compute_metrics=compute_metrics,
)

# ── 8. Train! ──
print("Starting fine-tuning...")
trainer.train()

# ── 9. Evaluate ──
results = trainer.evaluate()
print(f"\nFinal Accuracy: {results['eval_accuracy']*100:.1f}%")

# ── 10. Save model ──
trainer.save_model('../models/fine_tuned_model')
tokenizer.save_pretrained('../models/fine_tuned_model')
print("Model saved to ../models/fine_tuned_model ✅")

# ── 11. Detailed report ──
predictions = trainer.predict(val_dataset)
preds = np.argmax(predictions.predictions, axis=-1)
print("\nClassification Report:")
print(classification_report(
    val_labels, preds,
    target_names=['negative', 'neutral', 'positive']
))