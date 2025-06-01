import os
import base64
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, ChatMessage

# 配置模型
os.environ['OPENAI_API_KEY'] = 'none'
os.environ['OPENAI_BASE_URL'] = 'http://117.50.27.250:11434/v1'

# 初始化多模态模型
llm = ChatOpenAI(
    temperature=0,
    model_name='qwen2:7b'  # 假设该模型支持多模态，否则需更换为多模态版本
)


def encode_image(image_path: str) -> str:
    """将图片转换为 Base64 编码"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def analyze_image(image_path: str, prompt: str = "这张图片展示了什么？") -> str:
    """分析图片内容并返回描述"""
    try:
        # 编码图片
        base64_image = encode_image(image_path)

        # 构造多模态消息（遵循 OpenAI API 格式）
        messages = [
            HumanMessage(
                content=[
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            )
        ]

        # 调用模型
        response = llm(messages)
        return response.content

    except Exception as e:
        print(f"图片分析出错: {e}")
        return "抱歉，图片分析失败。"


# 示例使用
if __name__ == "__main__":
    image_path = "example.jpg"  # 替换为实际图片路径
    prompt = "图片中的动物是什么？它在做什么？"

    print(f"分析图片: {image_path}")
    print(f"提示: {prompt}")
    analysis = analyze_image(image_path, prompt)
    print(f"分析结果: {analysis}")