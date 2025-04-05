from transformers import (
    BertTokenizer, 
    BertForSequenceClassification,
    TrainingArguments,
    Trainer 
)
import torch
from sklearn.metrics import accuracy_score, f1_score
import numpy as np
from django.conf import settings

def load_model(model_name=None):
    """Загружает модель из настроек Django"""
    model_name = getattr(settings, 'BERT_MODEL_NAME', 'DeepPavlov/rubert-base-cased')
    tokenizer = BertTokenizer.from_pretrained(model_name)
    model = BertForSequenceClassification.from_pretrained(model_name, num_labels=2)
    return model, tokenizer

def predict_fake(text, model, tokenizer):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    probs = torch.softmax(outputs.logits, dim=1)
    return probs[0][1].item()  # Вероятность класса "фейк"

def compute_metrics(pred):
    labels = pred.label_ids
    preds = np.argmax(pred.predictions, axis=1)
    return {
        'accuracy': accuracy_score(labels, preds),
        'f1': f1_score(labels, preds)
    }

class BertTrainer:
    def __init__(self, model_name='DeepPavlov/rubert-base-cased'):
        self.model = BertForSequenceClassification.from_pretrained(model_name, num_labels=2)
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
    
    def train(self, train_dataset, val_dataset, output_dir='./models'):
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=3,
            per_device_train_batch_size=8,
            evaluation_strategy='epoch',
            save_strategy='epoch',
            logging_dir='./logs',
            load_best_model_at_end=True,
            metric_for_best_model='f1'
        )
        
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            compute_metrics=compute_metrics
        )
        
        trainer.train()
        self.model.save_pretrained(f"{output_dir}/finetuned_rubert")
        self.tokenizer.save_pretrained(f"{output_dir}/finetuned_rubert")