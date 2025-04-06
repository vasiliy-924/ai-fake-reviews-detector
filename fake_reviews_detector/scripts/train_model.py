# scripts/train_model.py
# Инициализация Django ДО всех импортов
import os

import django
import pandas as pd
from django.conf import settings
from reviews.ml.bert_model import BertTrainer
from reviews.ml.dataset import ReviewDataset
from reviews.ml.preprocessing import DatasetBuilder
from sklearn.model_selection import train_test_split
from transformers import TrainingArguments

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "fake_reviews_detector.settings")

django.setup()

# Остальные импорты после инициализации


def main():
    # Инициализация Django
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        "fake_reviews_detector.settings")
    import django

    django.setup()

    # Подготовка данных
    df = DatasetBuilder.build_dataframe()
    if len(df) < 500:
        raise ValueError(
            f"Недостаточно данных. Требуется 500+, получено {len(df)}")

    # Разделение данных
    train_df, val_df = train_test_split(
        df, test_size=0.2, random_state=42, stratify=df["label"]
    )

    # Конфигурация обучения для CPU
    training_args = TrainingArguments(
        output_dir=os.path.join(settings.BASE_DIR, "models"),
        num_train_epochs=3,
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        learning_rate=2e-5,
        warmup_steps=100,
        weight_decay=0.01,
        logging_steps=50,
        evaluation_strategy="steps",
        eval_steps=200,
        save_steps=500,
        fp16=False,
        dataloader_num_workers=0,  # Было 2 вернуть при необходимости
        report_to="none",
        disable_tqdm=False,  # Включаем прогресс-бар
    )

    # Инициализация тренера с аргументами
    trainer = BertTrainer(training_args=training_args)

    # Подготовка датасетов
    train_dataset = ReviewDataset(
        texts=train_df.text.tolist(),
        labels=train_df.label.tolist(),
        tokenizer=trainer.tokenizer,
    )

    val_dataset = ReviewDataset(
        texts=val_df.text.tolist(),
        labels=val_df.label.tolist(),
        tokenizer=trainer.tokenizer,
    )

    # Запуск обучения
    trainer.train(
        train_dataset=train_dataset,
        val_dataset=val_dataset,
        output_dir=os.path.join(settings.BASE_DIR, "models/finetuned_rubert"),
    )


if __name__ == "__main__":
    main()
