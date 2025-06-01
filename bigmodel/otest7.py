import base64
from io import BytesIO

from PIL import Image
from openai import OpenAI

client = OpenAI(
    base_url='http://117.50.27.250/v1',
    api_key='1q2w3e4r5t6y7u8i9o',  # required but ignored
)
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
def compress_and_convert(file_path, max_size=(100, 100), quality=85):
    """压缩图像并转换为Base64"""
    pil_image = Image.open(file_path)
    pil_image.thumbnail(max_size, Image.LANCZOS)
    buffered = BytesIO()
    pil_image.convert("RGB").save(buffered, format="JPEG", quality=quality)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

text = '我听到了一声巨响，大家快跑'

prompt = "图片里面有什么?"
image_path = '1.png'
# with open(image_path, "rb") as image_file:
#     b64_image = base64.b64encode(image_file.read()).decode("utf-8")

b64_image = compress_and_convert(image_path)
print(b64_image)
images = []
images.append(b64_image)


chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": '你是一个专业的舆情分析专家。请分析以下内容的情感倾向、潜在风险和敏感信息，并提供简要总结'
        },
        {
            "role": "user",
            "content": prompt,
            "images": images
                # [
                # {"type": "input_text", "text": prompt},
                # {
                #     "type": "images",
                #
                # },
        }
    ],

    model='llava',
    # model='qwen2.5:7b',
    max_tokens= 512,

)

print(chat_completion)
