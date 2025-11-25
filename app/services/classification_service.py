from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F

MODEL_NAME = "tabularisai/ModernFinBERT"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
model.eval()

id2label = model.config.id2label
label2id = {v.lower(): k for k, v in id2label.items()}

def calculate_polarity(p_positive: float, p_negative: float) -> float:
    denom = max(p_positive + p_negative, 1e-8)
    return (p_positive - p_negative) / denom

def get_sentiment(text: str) -> float:
    with torch.no_grad():
        inputs = tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=2048,
        )
        outputs = model(**inputs)
        probs = F.softmax(outputs.logits, dim=-1)[0].tolist()

    pos_idx = label2id["bullish"]
    neg_idx = label2id["bearish"]

    p_positive = probs[pos_idx]
    p_negative = probs[neg_idx]
    polarity = calculate_polarity(p_positive, p_negative)

    return round(polarity, 4)
