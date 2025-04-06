import os

import numpy as np
import torch
from django.conf import settings
from sklearn.metrics import accuracy_score, f1_score
from transformers import (BertForSequenceClassification, BertTokenizer,
                          Trainer, TrainingArguments)

device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")


def load_model():
    model_path = settings.BERT_MODEL_PATH  # Используем абсолютный путь

    # Явная проверка существования модели
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model directory {model_path} not found!")

    # Загрузка с локального пути
    tokenizer = BertTokenizer.from_pretrained(model_path)
    model = BertForSequenceClassification.from_pretrained(model_path)
    return model, tokenizer


def predict_fake(text, model, tokenizer):
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=512)
    # Перемещаем данные на устройство
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        outputs = model(**inputs)
    probs = torch.softmax(outputs.logits, dim=1)
    return probs[0][1].item()  # Вероятность класса "фейк"


def compute_metrics(pred):
    labels = pred.label_ids
    preds = np.argmax(pred.predictions, axis=1)
    return {"accuracy": accuracy_score(
        labels, preds), "f1": f1_score(labels, preds)}


class BertTrainer:
    def __init__(self, model_name="DeepPavlov/rubert-base-cased",
                 training_args=None):
        self.model = BertForSequenceClassification.from_pretrained(model_name)
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        self.model.to(device)
        self.training_args = (
            training_args or self.get_default_args()
        )  # Дефолтные аргументы

    def get_default_args(self):
        """Возвращает базовые параметры, если не переданы явно"""
        return TrainingArguments(
            output_dir="./results", per_device_train_batch_size=8, num_train_epochs=3
        )

    def train(self, train_dataset, val_dataset, output_dir):
        self.training_args.output_dir = output_dir  # Переопределяем выходную директорию
        trainer = Trainer(
            model=self.model,
            args=self.training_args,  # Используем переданные аргументы
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
        )
        trainer.train()
        self.model.save_pretrained(output_dir)
        self.tokenizer.save_pretrained(output_dir)
