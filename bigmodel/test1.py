import os
from langchain_openai import ChatOpenAI
os.environ['OPENAI_API_KEY'] = 'none'
os.environ['OPENAI_BASE_URL'] = 'http://117.50.27.250:11434/v1'
# 使用qwen2-7b（实际为in4量化版本)
llm = ChatOpenAI(temperature=0, model_name='qwen2:7b')

 