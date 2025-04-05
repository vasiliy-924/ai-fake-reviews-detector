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
    def __init__(self, model_name='DeepPavlov/rubert-base-cased', training_args=None):
        self.model = BertForSequenceClassification.from_pretrained(model_name)
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        self.training_args = training_args or self.get_default_args()  # Дефолтные аргументы

    def get_default_args(self):
        """Возвращает базовые параметры, если не переданы явно"""
        return TrainingArguments(
            output_dir="./results",
            per_device_train_batch_size=8,
            num_train_epochs=3
        )

    def train(self, train_dataset, val_dataset, output_dir):
        self.training_args.output_dir = output_dir  # Переопределяем выходную директорию
        trainer = Trainer(
            model=self.model,
            args=self.training_args,  # Используем переданные аргументы
            train_dataset=train_dataset,
            eval_dataset=val_dataset
        )
        trainer.train()
        self.model.save_pretrained(output_dir)
        self.tokenizer.save_pretrained(output_dir)