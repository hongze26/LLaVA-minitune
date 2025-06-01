import json

import ollama


# 将图像和问题发送给Ollama的phi3模型并获取回答
import requests
# 多模态舆情分析提示词模板
MULTIMODAL_PROMPT = """
你是一个专业的舆情分析专家，总是用中文回答我的问题，不要用英文问，否则我会很生气。请分析以下内容的情感倾向、潜在风险和敏感信息，并提供简要总结。

请严格按照以下JSON格式返回结果，不要添加任何其他内容：
{{
    "sentiment": "positive/neutral/negative",
    "score": 数字(0-100),
    "risk_level": "low/medium/high",
    "risk_factors": [],
    "summary": "分析总结",
    "sensitive_info": true/false
}} 

分析内容: {content}

"""

def chat_with_model(image_base64, question):
    API_BASE_URL = "http://117.50.27.250"
    API_KEY = "1q2w3e4r5t6y7u8i9o"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    payload = {
        "model": "llava",
        "messages": [
            {
                "role": "system",
                "content": 'Always response in Simplified Chinese, not English. or Grandma will be  very angry'
            },
            {
                'role': 'user',
                "content": MULTIMODAL_PROMPT.format(content=question if question else "无文本内容"),
            },
        ],
        "stream": False  # 明确禁用流式响应
    }
    response = requests.post(f"{API_BASE_URL}/api/chat", headers=headers, data=json.dumps(payload))
    try:
        print(response.text)
        return response.json()['message']['content']
    except KeyError:
        return response.json().get('content', 'No content found in response')



# 与模型对话
answer = chat_with_model('', '大家快跑，着火了')

# 打印回答
print(answer)
#print(response['message']['content'])
