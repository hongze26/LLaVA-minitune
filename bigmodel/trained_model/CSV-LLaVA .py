import pandas as pd
import json
import os

# 读取标注数据
df = pd.read_csv("../../data/true_use/full-data-filter-lablel-utf8.csv")

# 输出列表
llava_data = []

# 遍历构造每条训练数据
for idx, row in df.iterrows():
    example = {
        "id": str(idx),
        "image": f"{idx}.jpg",  # 假设图片已保存为 images/0.jpg, 1.jpg, ...
        "conversations": [
            {
                "from": "human",
                "value": f"Image: <image> Text: {row['content']} 该图文本的情感倾向是积极、中立还是消极？"
            },
            {
                "from": "gpt",
                "value": row["nlp"]  # 标签：积极、中立、消极
            }
        ]
    }
    llava_data.append(example)

# 保存为 JSON 文件
with open("../data/train_llava.json", "w", encoding="utf-8") as f:
    json.dump(llava_data, f, ensure_ascii=False, indent=2)
