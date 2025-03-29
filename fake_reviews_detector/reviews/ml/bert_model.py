from transformers import (
    BertTokenizer, 
    BertForSequenceClassification, 
)
import torch

def load_model():
    model_name = 'DeepPavlov/rubert-base-cased'
    tokenizer = BertTokenizer.from_pretrained(model_name)
    model = BertForSequenceClassification.from_pretrained(model_name, num_labels=2)
    return model, tokenizer

def predict_fake(text, model, tokenizer):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    probs = torch.softmax(outputs.logits, dim=1)
    return probs[0][1].item()  # Вероятность класса "фейк"
