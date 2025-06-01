import os
import argparse
import base64
import json
import requests
from typing import Dict, Any, Optional, List, Union
from PIL import Image


class OllamaClient:
    """Ollama API 客户端，支持文本和多模态模型"""

    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """
        初始化 Ollama API 客户端

        Args:
            base_url: API 基础 URL
            api_key: API 密钥
        """
        self.base_url = base_url.rstrip('/')
        self.headers = {}
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"

    def _make_request(self, endpoint: str, method: str = "GET",
                      data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """发送 API 请求并处理响应"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            else:
                raise ValueError(f"不支持的 HTTP 方法: {method}")

            # 检查 HTTP 状态码
            response.raise_for_status()

            # 解析 JSON 响应
            return response.json()

        except requests.exceptions.HTTPError as e:
            print(f"HTTP 错误: {e}")
            if response.content:
                try:
                    print(f"错误详情: {response.json()}")
                except json.JSONDecodeError:
                    print(f"错误详情: {response.text}")
            return {"error": str(e)}
        except requests.exceptions.RequestException as e:
            print(f"请求异常: {e}")
            return {"error": str(e)}
        except json.JSONDecodeError as e:
            print(f"JSON 解析错误: {e}")
            return {"error": str(e)}

    def list_models(self) -> Dict[str, Any]:
        """获取可用模型列表"""
        return self._make_request("api/tags")

    def generate(self, model: str, messages: List[Dict[str, Any]],
                 stream: bool = False) -> Dict[str, Any]:
        """
        使用聊天格式生成响应

        Args:
            model: 模型名称
            messages: 消息列表，每个消息是一个字典，包含 role 和 content
            stream: 是否使用流式响应

        Returns:
            API 响应
        """
        data = {
            "model": model,
            "messages": messages,
            "stream": stream
        }
        return self._make_request("api/chat", method="POST", data=data)

    def pull_model(self, model: str) -> Dict[str, Any]:
        """拉取模型"""
        data = {
            "name": model,
            "stream": False
        }
        return self._make_request("api/pull", method="POST", data=data)

    def show_model_info(self, model: str) -> Dict[str, Any]:
        """获取模型详细信息"""
        data = {
            "name": model
        }
        return self._make_request("api/show", method="POST", data=data)


def encode_image(image_path: str, max_size: int = 1024, quality: int = 80) -> str:
    """
    将图片编码为 Base64 字符串并压缩

    Args:
        image_path: 图片路径
        max_size: 图片最大尺寸（像素）
        quality: 图片质量（1-100）

    Returns:
        Base64 编码的图片字符串
    """
    try:
        # 打开图片
        img = Image.open(image_path)

        # 计算图片尺寸并压缩
        width, height = img.size
        if width > max_size or height > max_size:
            ratio = min(max_size / width, max_size / height)
            img = img.resize((int(width * ratio), int(height * ratio)), Image.LANCZOS)

        # 转换为RGB模式
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

        # 计算压缩后的大小
        original_size = os.path.getsize(image_path) / 1024
        compressed_size = len(encoded) * 3 / 4 / 1024

        print(f"图片压缩: {original_size:.2f}KB → {compressed_size:.2f}KB ({quality}%质量, 最大尺寸{max_size}px)")

        return encoded
    except Exception as e:
        print(f"图片处理错误: {e}")
        return ""


def create_multimodal_messages(text: str, image_path: Optional[str] = None,
                               max_size: int = 1024, quality: int = 80) -> List[Dict[str, Any]]:
    """
    创建多模态消息列表

    Args:
        text: 文本内容
        image_path: 图片路径（可选）
        max_size: 图片最大尺寸
        quality: 图片质量

    Returns:
        消息列表
    """
    messages = []

    # 系统提示
    system_prompt = {
        "role": "system",
        "content": "你是一个智能助手，能够理解文本和图像信息。"
    }
    messages.append(system_prompt)

    # 用户消息
    user_content = []
    if text:
        user_content.append({"type": "text", "text": text})

    if image_path:
        if os.path.exists(image_path):
            encoded_image = encode_image(image_path, max_size, quality)
            if encoded_image:
                user_content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}
                })
        else:
            print(f"图片不存在: {image_path}")

    if user_content:
        messages.append({"role": "user", "content": user_content})

    return messages


def main():
    parser = argparse.ArgumentParser(description="增强版 Ollama API 客户端")
    parser.add_argument("--url", default="http://117.50.27.250", help="Ollama API 基础 URL")
    parser.add_argument("--api-key", default="1q2w3e4r5t6y7u8i9o", help="API 密钥")
    parser.add_argument("--model", default="qwen2", help="使用的模型名称")
    parser.add_argument("--text", default="你好", help="输入的文本")
    parser.add_argument("--image", help="1.png")
    parser.add_argument("--max-size", type=int, default=1024, help="图片最大尺寸（像素）")
    parser.add_argument("--quality", type=int, default=80, help="图片质量（1-100）")
    parser.add_argument("--list-models", action="store_true", help="列出所有可用模型")
    parser.add_argument("--model-info", action="store_true", help="显示模型详细信息")
    args = parser.parse_args()

    print(f"Ollama API 客户端: {args.url}")
    if args.api_key:
        print("使用 API Key 认证")

    client = OllamaClient(args.url, args.api_key)

    # 列出可用模型
    if args.list_models:
        print("\n=== 可用模型列表 ===")
        models = client.list_models()
        if "error" in models:
            print(f"获取模型列表失败: {models['error']}")
        else:
            print(f"找到 {len(models.get('models', []))} 个模型")
            for model in models.get('models', []):
                print(f"- {model.get('name')}")
            return

    # 显示模型信息
    if args.model_info:
        print(f"\n=== 模型详情: {args.model} ===")
        info = client.show_model_info(args.model)
        if "error" in info:
            print(f"获取模型信息失败: {info['error']}")
        else:
            print(f"名称: {info.get('name')}")
            print(f"描述: {info.get('description')}")
            print(f"参数: {info.get('parameters')}")
            print(f"上下文窗口: {info.get('context_size')} tokens")
            print(f"文件大小: {info.get('size') / (1024 * 1024):.2f} MB")
            return

    # 创建消息列表
    messages = create_multimodal_messages(args.text, args.image, args.max_size, args.quality)

    if not messages or len(messages) < 2:
        print("错误: 没有有效的输入内容")
        return

    # 生成响应
    print(f"\n=== 使用模型 {args.model} 生成响应 ===")
    result = client.generate(args.model, messages)

    if "error" in result:
        print(f"生成失败: {result['error']}")
        if "model not found" in result['error'].lower():
            print("\n=== 尝试拉取模型 ===")
            pull_result = client.pull_model(args.model)
            if "error" in pull_result:
                print(f"拉取模型失败: {pull_result['error']}")
            else:
                print(f"模型 {args.model} 拉取成功")
                print("\n=== 再次尝试生成 ===")
                result = client.generate(args.model, messages)
                if "error" in result:
                    print(f"再次生成失败: {result['error']}")
    else:
        # 显示生成结果
        full_response = result.get('message', {}).get('content', '')
        print(f"生成结果: {full_response}")


if __name__ == "__main__":
    main()