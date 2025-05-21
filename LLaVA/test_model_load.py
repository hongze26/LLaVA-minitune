import torch
from transformers import AutoTokenizer, CLIPVisionModel
from llava.model import LlavaLlamaForCausalLM

model_path = "./checkpoints/llava-v1.5-7b"
vision_path = "./checkpoints/clip-vit-large-patch14-336"

print("🔄 加载 tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(model_path)

print("🔄 加载 LLaVA 模型...")
model = LlavaLlamaForCausalLM.from_pretrained(
    model_path,
    torch_dtype=torch.float16,
    device_map="auto"
)

print("🔄 加载视觉塔...")
vision_model = CLIPVisionModel.from_pretrained(
    vision_path,
    torch_dtype=torch.float16,
    device_map="auto"
)

print("✅ 模型和视觉塔加载成功！")
