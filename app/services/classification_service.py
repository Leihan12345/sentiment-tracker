from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F

tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
model.eval()

# Build a robust label->index map (e.g., {'negative':0, 'neutral':1, 'positive':2})
id2label = model.config.id2label
label2id = {v.lower(): k for k, v in id2label.items()}

def get_sentiment(text: str):
    with torch.no_grad():
        inputs = tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=512
        )
        outputs = model(**inputs)
        probs = F.softmax(outputs.logits, dim=-1)[0].tolist()

    pos_idx = label2id["positive"]
    neg_idx = label2id["negative"]

    p_positive = probs[pos_idx]
    p_negative = probs[neg_idx]
    polarity = calculate_polarity(p_positive, p_negative)

    return round(polarity, 4)

def calculate_polarity(p_positive: float, p_negative: float) -> float:
    denom = max(p_positive + p_negative, 1e-8)
    return (p_positive - p_negative) / denom