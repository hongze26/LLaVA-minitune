import json

a = '''json
{
    "sentiment": "neutral",
    "score": 50,
    "risklevel": "low",
    "riskfactors": [],
    "summary": "文本内容中没有明显的情感倾向，但是应该避免将其用于敏感信息的处理。",
    "sensitiveinfo": false
}
'''
b = json.loads(a.replace('json', ''))
print(b)