### colab 실행용 / 작동 안 됨 ###

import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
    DataCollatorForLanguageModeling,
)
from sklearn.metrics import accuracy_score, f1_score
from datasets import Dataset, DatasetDict
import json
import os
from peft import LoraConfig, get_peft_model

# Load tokenizer and model
model_id = "meta-llama/Meta-Llama-3-8B"
tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)

if tokenizer.pad_token is None:
    tokenizer.add_special_tokens({"pad_token": "[PAD]"})

# Load the model without LoRa to wrap it afterward
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    device_map="auto",
    offload_folder="offload",
    offload_state_dict=True,
    trust_remote_code=True,
)
model.resize_token_embeddings(len(tokenizer))

# Define LoRa configuration
lora_config = LoraConfig(
    r=16,                         # LoRa rank; adjust as needed
    lora_alpha=32,                # Scaling factor
    target_modules=["q_proj", "v_proj"],  # Specify attention layers
    lora_dropout=0.1,             # Dropout for LoRa layers
    bias="none"
)

# Wrap the model with LoRa
model = get_peft_model(model, lora_config)

# Load multiple JSON files from the folder
data_folder = "dbs/training/supreme_pansi_quiz/short_answer_splitted"
all_data = {"id": [], "판시사항": [], "판시결론_객관식": []}

# Iterate over each file in the folder
for filename in os.listdir(data_folder):
    if filename.endswith(".json"):
        file_path = os.path.join(data_folder, filename)
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            for element in data:
                # Check if "판시결론_객관식" exists and has exactly one element
                if "판시결론_객관식" in element and len(element["판시결론_객관식"]) == 1:
                    all_data["id"].append(element["id"])
                    all_data["판시사항"].append(element["판시사항"])
                    # Extract the single element and append it as a string
                    single_value = element["판시결론_객관식"][0]
                    all_data["판시결론_객관식"].append(str(single_value))

# Create a dataset from the collected data
dataset = Dataset.from_dict(all_data)

# Preprocessing function to tokenize input and output
def preprocess_data(examples):
    inputs = tokenizer(
        examples["판시사항"], truncation=True, padding="max_length", max_length=512
    )
    labels = tokenizer(
        examples["판시결론_객관식"], truncation=True, padding="max_length", max_length=128
    )
    inputs["labels"] = labels["input_ids"]
    return inputs

# Apply preprocessing
dataset = dataset.map(preprocess_data, batched=True)

# Split dataset (for fine-tuning purposes)
train_test_split = dataset.train_test_split(test_size=0.2)
dataset_dict = DatasetDict(
    {"train": train_test_split["train"], "test": train_test_split["test"]}
)

# Data collator for dynamic padding
data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

# Evaluation function
def compute_metrics(pred):
    predictions = torch.argmax(pred.predictions[0], dim=-1)
    labels = pred.label_ids
    # Flatten predictions and labels
    predictions = predictions.view(-1)
    labels = labels.view(-1)
    # Mask padding tokens
    mask = labels != -100
    predictions = predictions[mask]
    labels = labels[mask]
    accuracy = accuracy_score(labels.cpu().numpy(), predictions.cpu().numpy())
    f1 = f1_score(
        labels.cpu().numpy(), predictions.cpu().numpy(), average="weighted"
    )
    return {"accuracy": accuracy, "f1": f1}

# Define TrainingArguments for fine-tuning and evaluation
training_args = TrainingArguments(
    output_dir="./results",
    eval_strategy="epoch",
    per_device_train_batch_size=1,
    per_device_eval_batch_size=1,
    num_train_epochs=3,
    weight_decay=0.01,
)

# Initialize the Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset_dict["train"],
    eval_dataset=dataset_dict["test"],
    tokenizer=tokenizer,
    data_collator=data_collator,
    compute_metrics=compute_metrics,
)

# 1. Evaluation without fine-tuning
print("Evaluating without fine-tuning...")
eval_results = trainer.evaluate()
print(
    f"Accuracy: {eval_results['eval_accuracy']}, F1 Score: {eval_results['eval_f1']}"
)

# 2. Fine-tuning the model
print("Fine-tuning the model with LoRa...")
trainer.train()

# 3. Evaluation after fine-tuning
print("Evaluating after LoRa fine-tuning...")
eval_results_ft = trainer.evaluate()
print(
    f"LoRa Fine-tuned Accuracy: {eval_results_ft['eval_accuracy']}, LoRa Fine-tuned F1 Score: {eval_results_ft['eval_f1']}"
)
