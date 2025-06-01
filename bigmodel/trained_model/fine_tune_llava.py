from transformers import LlamaForCausalLM, LlamaTokenizer, Trainer, TrainingArguments
from datasets import load_dataset
from peft import LoraConfig, get_peft_model

# 加载模型和分词器
model_name = "llava"
model = LlamaForCausalLM.from_pretrained(model_name)
tokenizer = LlamaTokenizer.from_pretrained(model_name)

# 配置LoRA参数
config = LoraConfig(
    task_type='CAUSAL_LM',
    target_modules=["q_proj", "v_proj"],
    r=8,
    lora_alpha=32,
    lora_dropout=0.1
)
model = get_peft_model(model, config)

# 加载数据集
dataset = load_dataset("json", data_files="training_data.json")

# 数据预处理
def preprocess_function(examples):
    inputs = examples["prompt"]
    targets = examples["completion"]
    model_inputs = tokenizer(inputs, max_length=64, truncation=True)
    with tokenizer.as_target_tokenizer():
        labels = tokenizer(targets, max_length=64, truncation=True)
    model_inputs["labels"] = labels["input_ids"]
    return model_inputs

tokenized_datasets = dataset.map(preprocess_function, batched=True)

# 设置训练参数
training_args = TrainingArguments(
    output_dir="./results",
    evaluation_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=4,
    num_train_epochs=3,
    weight_decay=0.01,
)

# 使用Trainer进行训练
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets["train"],
)

trainer.train()