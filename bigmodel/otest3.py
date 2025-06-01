from ollama import Client
import json
import argparse
from typing import List, Dict, Any, Tuple
import base64
import os
from PIL import Image, ImageOps
import io


class SentimentAnalyzer:
    def __init__(self, base_url: str, model: str, api_key: str, image_quality: int = 85):
        """初始化舆情分析器"""
        self.client = Client(
            host=base_url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
        )
        self.model = model
        self.image_quality = image_quality  # 图片压缩质量（1-100）
        self.max_image_size = (1024, 1024)  # 最大尺寸（宽, 高）

        # 定义情感分析的提示词模板 - 支持文本和图片
        self.prompt_template = """
        请对以下内容进行舆情分析，从情感倾向、风险等级和关键信息三个方面进行评估：
        1. 情感倾向：正面、负面、中性
        2. 风险等级：高、中、低、无
        3. 关键信息：用简洁的语言提炼内容中的核心信息

        请按照以下JSON格式返回结果：
        {{
            "sentiment": "正面/负面/中性",
            "risk_level": "高/中/低/无",
            "key_points": ["关键点1", "关键点2"]
        }}

        内容信息：{content_info}
        """

    def _compress_image(self, image_path: str) -> bytes:
        """压缩图片并返回Base64编码数据"""
        try:
            with Image.open(image_path) as img:
                # 保持宽高比缩放图片
                img.thumbnail(self.max_image_size, Image.LANCZOS)

                # 转换为RGB格式（处理PNG透明背景）
                if img.mode != 'RGB':
                    img = img.convert('RGB')

                # 内存中保存压缩后的图片
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=self.image_quality)
                return buffer.getvalue()
        except Exception as e:
            print(f"图片压缩失败: {e}")
            raise

    def _prepare_content_info(self, text: str, image_path: str = None) -> str:
        """准备内容信息，处理文本和压缩后的图片"""
        content_parts = []

        if text:
            content_parts.append(f"文本内容：{text}")

        if image_path:
            try:
                # 压缩图片并获取Base64编码
                image_data = base64.b64encode(self._compress_image(image_path)).decode("utf-8")
                image_info = {
                    "type": "image",
                    "data": image_data
                }
                content_parts.append(f"图片信息：{json.dumps(image_info)}")
            except Exception as e:
                content_parts.append(f"文本内容：{text}\n图片处理错误：{str(e)}")

        return "\n".join(content_parts)

    def analyze(self, text: str = None, image_path: str = None) -> Dict[str, Any]:
        """分析文本和/或图片的舆情"""
        if not text and not image_path:
            return {
                "sentiment": "分析失败",
                "risk_level": "分析失败",
                "key_points": ["错误：必须提供文本或图片"]
            }

        content_info = self._prepare_content_info(text, image_path)
        prompt = self.prompt_template.format(content_info=content_info)

        try:
            response = self.client.chat(
                model=self.model,
                messages=[
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ]
            )
            # 解析模型返回的JSON结果
            return json.loads(response['message']['content'])
        except json.JSONDecodeError:
            # 如果模型返回的不是有效的JSON，进行简单处理
            content = response['message']['content']
            return {
                "sentiment": "无法判断",
                "risk_level": "无法判断",
                "key_points": [f"模型返回非结构化内容: {content}"]
            }
        except Exception as e:
            print(f"分析出错: {e}")
            return {
                "sentiment": "分析失败",
                "risk_level": "分析失败",
                "key_points": [str(e)]
            }

    def batch_analyze(self, items: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """批量分析舆情，每个item包含text和/或image_path"""
        results = []
        for item in items:
            text = item.get("text")
            image_path = item.get("image_path")
            result = self.analyze(text, image_path)
            results.append({
                "text": text,
                "image_path": image_path,
                "analysis": result
            })
        return results

    def analyze_from_file(self, file_path: str) -> List[Dict[str, Any]]:
        """从文件读取内容并分析舆情
        文件格式：每行是一个JSON对象，包含text和/或image_path字段
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]

            items = []
            for line in lines:
                try:
                    item = json.loads(line)
                    items.append(item)
                except json.JSONDecodeError:
                    print(f"跳过无效JSON行: {line}")

            return self.batch_analyze(items)
        except Exception as e:
            print(f"读取文件出错: {e}")
            return []

    def generate_report(self, results: List[Dict[str, Any]], output_file: str = None) -> None:
        """生成舆情分析报告"""
        # 统计结果
        sentiment_counts = {
            "正面": 0,
            "负面": 0,
            "中性": 0,
            "无法判断": 0,
            "分析失败": 0
        }
        risk_counts = {
            "高": 0,
            "中": 0,
            "低": 0,
            "无": 0,
            "无法判断": 0,
            "分析失败": 0
        }

        for result in results:
            sentiment = result['analysis']['sentiment']
            risk = result['analysis']['risk_level']
            sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
            risk_counts[risk] = risk_counts.get(risk, 0) + 1

        # 生成报告
        report = {
            "total_analyzed": len(results),
            "sentiment_distribution": sentiment_counts,
            "risk_level_distribution": risk_counts,
            "detailed_results": results
        }

        # 输出报告
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"报告已保存到 {output_file}")
        else:
            print(json.dumps(report, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description='Ollama舆情分析工具')
    parser.add_argument('--text',default='大家快跑着火了', help='要分析的文本')
    parser.add_argument('--image',default='1.png', help='要分析的图片路径')
    parser.add_argument('--file', help='包含文本和图片信息的文件路径')
    parser.add_argument('--output', help='输出报告的文件路径')
    parser.add_argument('--quality', type=int, default=85, help='图片压缩质量（1-100，默认85）')
    args = parser.parse_args()

    # 配置Ollama API
    OLLAMA_BASE_URL = "http://117.50.27.250"  # 根据你的配置修改
    OLLAMA_MODEL = "bsahane/Qwen2.5-VL-7B-Instruct:Q4_K_M_benxh"  # 使用Qwen2多模态模型
    API_KEY = "1q2w3e4r5t6y7u8i9o"  # Ollama API密钥

    analyzer = SentimentAnalyzer(OLLAMA_BASE_URL, OLLAMA_MODEL, API_KEY, image_quality=args.quality)

    if args.text or args.image:
        # 分析单个文本或图片
        result = analyzer.analyze(args.text, args.image)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.file:
        # 从文件分析多个内容
        results = analyzer.analyze_from_file(args.file)
        analyzer.generate_report(results, args.output)
    else:
        print("请提供--text、--image或--file参数")


if __name__ == "__main__":
    main()