import os

def count_code_lines(directory):
    total = 0
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#'):
                                total += 1
                except Exception as e:
                    print(f"跳过无法读取的文件: {filepath}")
    return total

# 请修改为你的项目目录路径（Windows 风格路径，双反斜杠）
project_dir = r"E:\workspace\Public-opinion-analysis\opinion-analysis"
print("有效 Python 源代码行数：", count_code_lines(project_dir))
