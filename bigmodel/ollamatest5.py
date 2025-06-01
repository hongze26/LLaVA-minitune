import os
import argparse
import base64
import requests
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import numpy as np

# Ollama API 配置
OLLAMA_BASE_URL = "http://117.50.27.250"
MODEL_NAME = "qwen2"  # Qwen2 多模态模型
API_KEY = "1q2w3e4r5t6y7u8i9o"  # Ollama API密钥


def encode_image(image_path, max_size=1024, quality=80):
    """将图片编码为 Base64 字符串，支持压缩图片"""
    try:
        # 打开图片
        img = Image.open(image_path)

        # 获取原始图片大小
        original_size = os.path.getsize(image_path) / 1024  # KB

        # 计算图片尺寸并压缩
        width, height = img.size
        if width > max_size or height > max_size:
            ratio = min(max_size / width, max_size / height)
            img = img.resize((int(width * ratio), int(height * ratio)), Image.LANCZOS)

        # 转换为RGB模式（处理PNG等可能的其他模式）
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # 临时保存压缩后的图片
        temp_path = f"{image_path}.temp.jpg"
        img.save(temp_path, quality=quality, optimize=True)

        # 读取压缩后的图片并编码
        with open(temp_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode('utf-8')

        # 删除临时文件
        os.remove(temp_path)

        # 计算压缩后的图片大小
        compressed_size = len(encoded) * 3 / 4 / 1024  # KB (Base64膨胀约4/3)

        print(f"图片压缩: {original_size:.2f}KB → {compressed_size:.2f}KB ({quality}%质量, 最大尺寸{max_size}px)")

        return encoded
    except Exception as e:
        print(f"图片编码错误: {e}")
        return None


def analyze_sentiment(text, image_base64=None):
    """调用 Ollama API 分析文本和图片的舆情"""
    # 构建提示词
    system_prompt = """
    你是一个专业的舆情分析师。请根据提供的文本和图片，分析其中的情感倾向（积极、中性、消极），
    并给出简要的分析理由。格式为："情感倾向：积极/中性/消极\n分析理由：..."
    """

    # 构建消息列表
    messages = [{"role": "system", "content": system_prompt}]

    # 添加用户输入
    user_content = []
    if text:
        user_content.append({"type": "text", "text": text})
    if image_base64:
        user_content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
        })

    messages.append({"role": "user", "content": user_content})

    # 准备请求头和请求体
    headers = {}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"

    # 调用 Ollama API
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            headers=headers,
            json={
                "model": MODEL_NAME,
                "messages": messages,
                "stream": False
            }
        )
        response.raise_for_status()
        return response.json()["message"]["content"]
    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 401:
            print("API 认证失败：请检查你的 API Key 是否正确")
        else:
            print(f"HTTP 错误: {http_err}")
        return None
    except Exception as e:
        print(f"API 调用失败: {e}")
        return None


def parse_response(api_response):
    """解析 API 返回的结果，提取情感倾向和分析理由"""
    if not api_response:
        return "未知", "无法获取分析结果"

    lines = api_response.strip().split('\n')
    sentiment = "未知"
    reason = "未提供分析理由"

    for line in lines:
        if line.lower().startswith("情感倾向："):
            sentiment = line[5:].strip()
        elif line.lower().startswith("分析理由："):
            reason = line[5:].strip()

    return sentiment, reason


def visualize_sentiment(sentiment):
    """可视化情感分析结果"""
    # 定义情感分数
    sentiment_scores = {
        "积极": 100,
        "中性": 50,
        "消极": 0,
        "未知": 50
    }

    score = sentiment_scores.get(sentiment, 50)

    # 创建颜色映射
    cmap = LinearSegmentedColormap.from_list("sentiment_cmap", ["red", "gray", "green"])

    # 创建图表
    fig, ax = plt.subplots(figsize=(10, 2))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 1)

    # 绘制背景渐变
    for i in range(100):
        ax.axvline(x=i, color=cmap(i / 100), linewidth=10)

    # 绘制分数标记
    ax.axvline(x=score, color='white', linewidth=3, linestyle='--')
    ax.text(score, 0.5, f"{sentiment} ({score})",
            horizontalalignment='center',
            verticalalignment='center',
            fontsize=14,
            fontweight='bold',
            bbox=dict(facecolor='white', alpha=0.7))

    # 隐藏坐标轴
    ax.set_axis_off()

    plt.tight_layout()
    plt.savefig("sentiment_visualization.png", dpi=300, bbox_inches='tight')
    print("情感可视化结果已保存为 sentiment_visualization.png")


def main():
    """主函数，处理命令行参数并执行舆情分析"""
    parser = argparse.ArgumentParser(description='使用 Ollama + Qwen2 进行文本和图片舆情分析')
    parser.add_argument('--text', type=str, default='我是一个好人', help='要分析的文本内容')
    parser.add_argument('--image', type=str, default='1.png', help='要分析的图片路径')
    parser.add_argument('--max-size', type=int, default=1024, help='图片最大尺寸（像素）')
    parser.add_argument('--quality', type=int, default=80, help='图片质量（1-100）')

    args = parser.parse_args()

    # 处理图片
    image_base64 = None
    if args.image:
        if not os.path.exists(args.image):
            print(f"图片文件不存在: {args.image}")
            return
        image_base64 = encode_image(args.image, args.max_size, args.quality)
        if not image_base64:
            return

    # 分析舆情
    print("正在分析舆情...")
    api_response = analyze_sentiment(args.text, image_base64)

    # 解析结果
    sentiment, reason = parse_response(api_response)

    # 输出结果
    print("\n舆情分析结果:")
    print(f"舆情倾向: {sentiment}")
    print(f"分析理由: {reason}")

    # 可视化结果
    visualize_sentiment(sentiment)


if __name__ == "__main__":
    main()