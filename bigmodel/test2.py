import os
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

# 配置模型
os.environ['OPENAI_API_KEY'] = 'none'  # 本地服务无需密钥
os.environ['OPENAI_BASE_URL'] = 'http://117.50.27.250:11434/api/generate'

# 初始化模型（启用流式输出）
llm = ChatOpenAI(
    temperature=0,
    model_name='qwen2',
    streaming=True,
    callbacks=[StreamingStdOutCallbackHandler()]
)


def ask_question(question: str) -> str:
    """向 Qwen2 模型提问并获取回答"""
    try:
        # 构造消息列表
        messages = [HumanMessage(content=question)]

        # 调用模型（流式输出会直接打印）
        response = llm(messages)

        # 返回完整回答
        return response.content

    except Exception as e:
        print(f"提问出错: {e}")
        return "抱歉，回答生成失败。"


# 示例使用
if __name__ == "__main__":
    question = "请简要介绍量子计算的基本原理。"
    print(f"问题: {question}")
    print("回答:")
    answer = ask_question(question)