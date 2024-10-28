import torch
from transformers import LlamaForCausalLM, LlamaTokenizer, Trainer, TrainingArguments, DataCollatorForLanguageModeling
from sklearn.metrics import accuracy_score, f1_score
from datasets import Dataset, DatasetDict
import json
import os

# Load tokenizer and model
tokenizer = LlamaTokenizer.from_pretrained("huggingface/llama-2-7b")
model = LlamaForCausalLM.from_pretrained("huggingface/llama-2-7b").to("cuda")

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
                all_data["id"].append(element["id"])
                all_data["판시사항"].append(element["판시사항"])
                all_data["판시결론_객관식"].append(element["판시결론_객관식"])

# Create a dataset from the collected data
dataset = Dataset.from_dict(all_data)

# Preprocessing function to tokenize input and output
def preprocess_data(examples):
    inputs = tokenizer(examples["판시사항"], truncation=True, padding="max_length", max_length=512, return_tensors="pt")
    labels = tokenizer(examples["판시결론_객관식"], truncation=True, padding="max_length", max_length=128, return_tensors="pt")
    inputs["labels"] = labels["input_ids"]
    return inputs

# Apply preprocessing
dataset = dataset.map(preprocess_data, batched=True)

# Split dataset (for fine-tuning purposes)
train_test_split = dataset.train_test_split(test_size=0.2)
dataset_dict = DatasetDict({"train": train_test_split["train"], "test": train_test_split["test"]})

# Data collator for dynamic padding
data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

# Evaluation function
def compute_metrics(pred):
    predictions = torch.argmax(pred.predictions, dim=-1)
    labels = pred.label_ids
    accuracy = accuracy_score(labels, predictions)
    f1 = f1_score(labels, predictions, average="weighted")
    return {"accuracy": accuracy, "f1": f1}

# Define Trainer for fine-tuning and evaluation
training_args = TrainingArguments(
    output_dir="./results",
    evaluation_strategy="epoch",
    per_device_train_batch_size=1,
    per_device_eval_batch_size=1,
    num_train_epochs=3,
    weight_decay=0.01,
)

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
print(f"Accuracy: {eval_results['eval_accuracy']}, F1 Score: {eval_results['eval_f1']}")

# 2. Fine-tuning the model
print("Fine-tuning the model...")
trainer.train()

# 3. Evaluation after fine-tuning
print("Evaluating after fine-tuning...")
eval_results_ft = trainer.evaluate()
print(f"Fine-tuned Accuracy: {eval_results_ft['eval_accuracy']}, Fine-tuned F1 Score: {eval_results_ft['eval_f1']}")