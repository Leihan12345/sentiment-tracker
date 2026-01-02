import torch
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForMaskedLM,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments
)

# ===============================
# Configuration
# ===============================
MODEL_NAME = "tabularisai/ModernFinBERT"
DATASET_NAME = "SocialGrep/the-reddit-dataset-dataset"

TEXT_COLUMN = "body"
MAX_LENGTH = 256
NUM_SAMPLES = 30_000

OUTPUT_DIR = "./finbert_reddit"
BATCH_SIZE = 16
EPOCHS = 3
LR = 5e-5


dataset = load_dataset(DATASET_NAME, split="train")


dataset = dataset.filter(lambda x: x.get(TEXT_COLUMN) is not None and len(x[TEXT_COLUMN]) > 20)

dataset = dataset.shuffle(seed=42).select(range(NUM_SAMPLES))

dataset = dataset.train_test_split(test_size=0.05)

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_fast=True)

def tokenize(batch):
    return tokenizer(
        batch[TEXT_COLUMN],
        truncation=True,
        padding="max_length",
        max_length=MAX_LENGTH
    )

tokenized = dataset.map(
    tokenize,
    batched=True,
    remove_columns=dataset["train"].column_names
)

# ===============================
# Model
# ===============================
model = AutoModelForMaskedLM.from_pretrained(MODEL_NAME)

# ===============================
# Data Collator (MLM)
# ===============================
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=True,
    mlm_probability=0.15
)

# ===============================
# Training Args
# ===============================
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    overwrite_output_dir=True,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    learning_rate=LR,
    per_device_train_batch_size=BATCH_SIZE,
    per_device_eval_batch_size=BATCH_SIZE,
    num_train_epochs=EPOCHS,
    weight_decay=0.01,
    fp16=torch.cuda.is_available(),
    logging_steps=100,
    save_total_limit=2,
    load_best_model_at_end=True,
    report_to="none"
)

# ===============================
# Trainer
# ===============================
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized["train"],
    eval_dataset=tokenized["test"],
    tokenizer=tokenizer,
    data_collator=data_collator
)

# ===============================
# Train
# ===============================
trainer.train()

trainer.save_model(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)