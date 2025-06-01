from openai import OpenAI

client = OpenAI(
    base_url='http://117.50.27.250/v1/',
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

text = '我听到了一声巨响，大家快跑'
chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": '你是一个专业的舆情分析专家。请分析以下内容的情感倾向、潜在风险和敏感信息，并提供简要总结'
        },
        {
            "role": "user",
            "content": MULTIMODAL_PROMPT.format(content=text if text else "无文本内容"),
        }
    ],

    model='llava',
    # model='qwen2.5:7b',

    max_tokens=38192,
    temperature=0.7,
    top_p=0.5,
    frequency_penalty=0,
    presence_penalty=2,
)

print(chat_completion)
