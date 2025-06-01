from ollama import Client

# 自定义客户端，并填入远端服务器地址，默认是 127.0.0.1
client = Client(host='http://117.50.27.250:11434')  # 如果需要设置链接超时，可以使用 timeout 来进行设置

messages = [
    {
        'role': 'user',
        'content': 'Why is the sky blue?',
    },
]

response = client.chat(model='qwen2', messages=messages)
print(response['message']['content'])