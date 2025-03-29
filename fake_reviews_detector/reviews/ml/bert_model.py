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
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    outputs = model(**inputs)
    probs = torch.softmax(outputs.logits, dim=1)
    prob_fake = probs[0][1].item()
    print(f"Вероятность фейка: {prob_fake}")  # Должно выводить число (например, 0.83)
    return prob_fake
