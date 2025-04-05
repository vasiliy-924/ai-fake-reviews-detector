# scripts/train_model.py
import pandas as pd
from sklearn.model_selection import train_test_split
import torch
from reviews.ml.preprocessing import DatasetBuilder
from reviews.ml.dataset import ReviewDataset
from reviews.ml.bert_model import BertTrainer
import os
from django.conf import settings

def main():
    # Инициализация Django (обязательно!)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fake_reviews_detector.settings')
    import django
    django.setup()

    # Подготовка данных
    df = DatasetBuilder.build_dataframe()
    
    # Проверка данных
    if len(df) < 500:
        raise ValueError(f"Недостаточно данных для обучения. Требуется 500+, получено {len(df)}")
    
    train_df, val_df = train_test_split(df, test_size=0.2, random_state=42, stratify=df['label'])
    
    # Инициализация
    trainer = BertTrainer()
    
    # Датасеты
    train_dataset = ReviewDataset(
        texts=train_df.text.tolist(),
        labels=train_df.label.tolist(),
        tokenizer=trainer.tokenizer
    )
    
    val_dataset = ReviewDataset(
        texts=val_df.text.tolist(),
        labels=val_df.label.tolist(),
        tokenizer=trainer.tokenizer
    )
    
    # Обучение (путь сохраняется в settings.py)
    trainer.train(
        train_dataset=train_dataset,
        val_dataset=val_dataset,
        output_dir=os.path.join(settings.BASE_DIR, 'models/finetuned_rubert')  # Путь для сохранения
    )

if __name__ == "__main__":
    main()