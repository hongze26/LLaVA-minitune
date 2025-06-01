import os
import json
import base64
import requests
from PIL import Image
from io import BytesIO
import argparse

# 配置Ollama API
OLLAMA_BASE_URL = "http://117.50.27.250"  # 根据你的配置修改
OLLAMA_MODEL = "bsahane/Qwen2.5-VL-7B-Instruct:Q4_K_M_benxh"  # 使用Qwen2多模态模型
API_KEY = "1q2w3e4r5t6y7u8i9o"  # Ollama API密钥

# 多模态舆情分析提示词模板
MULTIMODAL_PROMPT = """
你是一个专业的舆情分析专家。请分析以下内容的情感倾向、潜在风险和敏感信息，并提供简要总结。

请严格按照以下JSON格式返回结果，不要添加任何其他内容：
{{
    "sentiment": "positive/neutral/negative",
    "score": 数字(0-100),
    "risk_level": "low/medium/high",
    "risk_factors": ["风险因素1", "风险因素2"],
    "summary": "分析总结",
    "sensitive_info": true/false
}}

分析内容: {content}
"""


def encode_image(image_path):
    """将图片编码为Base64格式，处理RGBA转RGB"""
    try:
        img = Image.open(image_path)
        # 处理RGBA -> RGB
        if img.mode == 'RGBA':
            img = img.convert('RGB')

        # 调整图片大小以减少数据量
        img.thumbnail((800, 800))
        buffered = BytesIO()
        img.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return img_str
    except Exception as e:
        print(f"Error encoding image: {e}")
        return None


def call_ollama_api(messages):
    """调用Ollama API进行多模态分析"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    data = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": 0.2,  # 低温度以获得更确定性的结果
            "stop": ["}"],  # 确保JSON响应完整性
            "format": "json"  # 指定返回JSON格式
        }
    }

    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        
        # 尝试提取JSON字符串
        content = response.json().get("message", {}).get("content", "")
        # 确保返回的是一个有效的JSON字符串
        if not content.strip().startswith("{"):
            return json.dumps({
                "error": "Invalid response format",
                "raw_response": content
            })
        return content
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "raw_response": "API调用失败"
        })


def analyze_text_and_image(text, image_path=None):
    """分析文本和图片的多模态舆情"""
    # 构建多模态消息
    messages = [
        {
            "role": "user",
            "content": MULTIMODAL_PROMPT.format(content=text if text else "无文本内容")
        }
    ]

    # 添加图片（如果有）
    if image_path:
        image_base64 = encode_image(image_path)
        if image_base64:
            # 根据Ollama的要求调整格式
            messages.append({
                "role": "user",
                "content": f"<|FunctionCallBegin|>[\{{\"name\":\"analyze_image\",\"parameters\":{{\"image\":\"data:image/jpeg;base64,{image_base64}\"}}}}\]<|FunctionCallEnd|>"
            })
        else:
            print("无法编码图片，仅分析文本")

    response = call_ollama_api(messages)

    try:
        # 尝试解析JSON结果
        return json.loads(response.strip())
    except json.JSONDecodeError:
        # 如果无法解析，返回原始文本
        return {
            "raw_response": response,
            "error": "Failed to parse JSON response from Ollama"
        }


def main():
    parser = argparse.ArgumentParser(description="文本与图片舆情分析工具")
    parser.add_argument("--text", default='我是好人', help="要分析的文本内容")
    parser.add_argument("--image", default='1.png', help="要分析的图片路径")


    args = parser.parse_args()

    if not args.text and not args.image:
        print("请至少提供文本或图片进行分析")
        return

    print("正在分析舆情...")
    result = analyze_text_and_image(args.text, args.image)

    # 打印结果
    print("\n舆情分析结果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))




if __name__ == "__main__":
    main()