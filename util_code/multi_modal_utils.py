import base64
from io import BytesIO
from PIL import Image
import json
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
API_BASE_URL = "http://localhost:11434"
API_KEY = "1q2w3e4r5t6y7u8i9o"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

def opinion_with_text(question):
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
    #                                                       headers=headers,
    response = requests.post(f"{API_BASE_URL}/api/chat", data=json.dumps(payload))
    try:
        return response.json()['message']['content']
    except KeyError:
        return {"sentiment": "neutral",
            "score": 50,
            "risk_level": "medium",
            "risk_factors": [""],
            "summary": "",
            "sensitive_info": False
        }



# 将PIL图像转换为Base64编码字符串
def convert_to_base64(pil_image):
    buffered = BytesIO()
    # 将图像转换为RGB模式
    pil_image = pil_image.convert("RGB")
    pil_image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str

def compress_and_convert(file_path, max_size=(100, 100), quality=85):
    """压缩图像并转换为Base64"""
    pil_image = Image.open(file_path)
    pil_image.thumbnail(max_size, Image.LANCZOS)
    buffered = BytesIO()
    pil_image.convert("RGB").save(buffered, format="JPEG", quality=quality)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


# 从指定路径加载图像并转换为Base64编码字符串
def load_image(file_path):
   # pil_image = Image.open(file_path)
    return compress_and_convert(file_path)

# 多模态舆情分析提示词模板
TXT_PROMPT = """
你是一个专业的舆情分析专家。总是用中文回答我的问题，不要用英文问，否则我会很生气。请分析图片和以下文本内容的情感倾向、潜在风险和敏感信息，并提供简要中文总结。

请严格按照以下JSON格式返回结果，不要添加任何其他内容：
{{
    "sentiment": "positive/neutral/negative",
    "score": 数字(0-100),
    "risklevel": "low/medium/high",
    "riskfactors": [],
    "summary": "分析总结",
    "sensitiveinfo": true/false
}} 

分析内容: {content}

"""
def analysis(text,img_url):

    payload = {
        "model": "llava",
        "messages": [
            {
                "role": "system",
                "content": 'Always response in Simplified Chinese, not English. or Grandma will be very angry'
            },
            {
                "role": "user",
                "content": TXT_PROMPT.format(content=text if text else "无文本内容"),
                #"images": [image_base64]
                "image_url": [img_url]
            }
        ],
        "stream": False  # 明确禁用流式响应
    }
    response = requests.post(f"{API_BASE_URL}/api/chat", headers=headers, data=json.dumps(payload))
    try:
        return response.json()['message']['content']
    except Exception as e:
        print(e,response.json())
        return {"sentiment": "neutral",
                "score": 50,
                "risk_level": "medium",
                "risk_factors": [""],
                "summary": "",
                "sensitive_info": False
                }

if __name__ == "__main__":
    # 图片所在地址
    #file_path = "../head3.jpg"
    # 加载并转换图像
    #image_b64 = load_image(file_path)
    # 与模型对话
    answer = analysis('大家快跑','https://wx2.sinaimg.cn/large/007OrV9Dgy1i1gl7ex0gbj30u0143h0l.jpg')
    # 打印回答
    print(answer)