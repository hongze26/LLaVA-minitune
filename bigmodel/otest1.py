from ollama import Client

# 配置Ollama API
OLLAMA_BASE_URL = "http://117.50.27.250"  # 根据你的配置修改
OLLAMA_MODEL = "bsahane/Qwen2.5-VL-7B-Instruct:Q4_K_M_benxh"  # 使用Qwen2多模态模型
API_KEY = "1q2w3e4r5t6y7u8i9o"  # Ollama API密钥


client = Client(
    host=OLLAMA_BASE_URL,
    headers={"Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"}
)

response = client.chat(model=OLLAMA_MODEL, messages=[
    {
        'role': 'user',
        'content': '你是谁?',
    },
])
print(response['message']['content'])