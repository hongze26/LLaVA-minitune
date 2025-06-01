import requests
import json
import argparse
from typing import Dict, Any, Optional


class OllamaClient:
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """
        初始化 Ollama API 客户端

        Args:
            base_url: API 基础 URL，例如 http://localhost:11434 或 https://your-domain.com
            api_key: API 密钥（如果配置了的话）
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
                raise ValueError(f"Unsupported HTTP method: {method}")

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

    def generate(self, model: str, prompt: str, stream: bool = False) -> Dict[str, Any]:
        """生成文本"""
        data = {
            "model": model,
            "prompt": prompt,
            "stream": stream
        }
        return self._make_request("api/generate", method="POST", data=data)

    def pull_model(self, model: str) -> Dict[str, Any]:
        """拉取模型"""
        data = {
            "name": model,
            "stream": False
        }
        return self._make_request("api/pull", method="POST", data=data)


def main():
    parser = argparse.ArgumentParser(description="Ollama API 测试工具")
    parser.add_argument("--url", default="http://117.50.27.250", help="Ollama API 基础 URL")
    parser.add_argument("--api-key", default="1q2w3e4r5t6y7u8i9o",help="API 密钥（如果有）")
    parser.add_argument("--model", default="qwen2", help="要测试的模型名称")
    parser.add_argument("--prompt", default="Hello, world!", help="测试提示词")
    args = parser.parse_args()

    print(f"测试 Ollama API: {args.url}")
    if args.api_key:
        print("使用 API Key 认证")

    client = OllamaClient(args.url, args.api_key)

    # 1. 测试获取模型列表
    print("\n=== 测试获取模型列表 ===")
    models = client.list_models()
    if "error" in models:
        print(f"获取模型列表失败: {models['error']}")
        return

    print(f"可用模型数量: {len(models.get('models', []))}")
    for model in models.get('models', [])[:3]:  # 只显示前3个模型
        print(f"- {model.get('name')} ({model.get('modified_at')})")

    # 2. 测试模型生成
    print(f"\n=== 测试模型生成 ({args.model}) ===")
    result = client.generate(args.model, args.prompt)
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
                result = client.generate(args.model, args.prompt)
                if "error" in result:
                    print(f"再次生成失败: {result['error']}")
                else:
                    print(f"生成成功: {result.get('response', '')[:50]}...")
        return

    # 显示生成结果
    full_response = result.get('response', '')
    print(f"生成结果: {full_response[:100]}...")  # 只显示前100个字符


if __name__ == "__main__":
    main()