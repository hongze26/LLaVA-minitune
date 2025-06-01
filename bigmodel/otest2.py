from ollama import Client
import json
import argparse
from typing import List, Dict, Any, Tuple


class SentimentAnalyzer:
    def __init__(self, base_url: str, model: str, api_key: str):
        """初始化舆情分析器"""
        self.client = Client(
            host=base_url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
        )
        self.model = model
        # 定义情感分析的提示词模板
        self.prompt_template = """
        请对以下文本进行舆情分析，从情感倾向、风险等级和关键信息三个方面进行评估：
        1. 情感倾向：正面、负面、中性
        2. 风险等级：高、中、低、无
        3. 关键信息：用简洁的语言提炼文本中的核心内容

        请按照以下JSON格式返回结果：
        {{
            "sentiment": "正面/负面/中性",
            "risk_level": "高/中/低/无",
            "key_points": ["关键点1", "关键点2"]
        }}

        文本内容：{text}
        """

    def analyze_text(self, text: str) -> Dict[str, Any]:
        """分析单个文本的舆情"""
        prompt = self.prompt_template.format(text=text)
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
            print(response)
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

    def batch_analyze(self, texts: List[str]) -> List[Dict[str, Any]]:
        """批量分析文本舆情"""
        results = []
        for text in texts:
            result = self.analyze_text(text)
            results.append({
                "text": text,
                "analysis": result
            })
        return results

    def analyze_from_file(self, file_path: str) -> List[Dict[str, Any]]:
        """从文件读取文本并分析舆情"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                texts = [line.strip() for line in f if line.strip()]
            return self.batch_analyze(texts)
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
        print(results)
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


        print(report)


def main():
    parser = argparse.ArgumentParser(description='Ollama舆情分析工具')
    parser.add_argument('--text',default='大家快跑着火了', help='要分析的文本')
    parser.add_argument('--file', help='包含文本的文件路径，每行一个文本')
    args = parser.parse_args()

    # 配置Ollama API
    OLLAMA_BASE_URL = "http://117.50.27.250"  # 根据你的配置修改
    OLLAMA_MODEL = "bsahane/Qwen2.5-VL-7B-Instruct:Q4_K_M_benxh"  # 使用Qwen2多模态模型
    API_KEY = "1q2w3e4r5t6y7u8i9o"  # Ollama API密钥

    analyzer = SentimentAnalyzer(OLLAMA_BASE_URL, OLLAMA_MODEL, API_KEY)

    if args.text:
        # 分析单个文本
        result = analyzer.analyze_text(args.text)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.file:
        # 从文件分析多个文本
        results = analyzer.analyze_from_file(args.file)
        analyzer.generate_report(results, args.output)
    else:
        print("请提供--text或--file参数")


if __name__ == "__main__":
    main()