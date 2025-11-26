import subprocess, sys, json, datetime
from pathlib import Path

BASE = Path(__file__).parent
runs_dir = BASE / "runs"
runs_dir.mkdir(exist_ok=True)
timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
work_dir = runs_dir / timestamp
work_dir.mkdir(parents=True, exist_ok=True)

json_path = work_dir / "qwen_essay_result.json"
pdf_path = work_dir / "essay_report.pdf"

def run(cmd):
    
    print(f"==> {cmd}")
    subprocess.check_call(cmd, shell=True)

# 1) 生成 JSON（根据你的 Qwen.py 实际参数修改）
run(f"{sys.executable} Qwen.py --out {json_path}")

# 2) 构建前端（如果 dist 已经存在且不用更新，可跳过）
run("npm run build")

# 3) 生成 PDF
run(f"node export-pdf.js --json={json_path} --out={pdf_path} --dist=./dist --port=4173")

# 4) 返回给前端/调用方
result = {"status": "ok", "json": str(json_path), "pdf": str(pdf_path)}
print(json.dumps(result))


# import subprocess
# import sys
# import json
# import datetime
# from pathlib import Path

# BASE = Path(__file__).parent
# runs_dir = BASE / "runs"
# runs_dir.mkdir(exist_ok=True)
# timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
# work_dir = runs_dir / timestamp
# work_dir.mkdir(parents=True, exist_ok=True)

# json_path = work_dir / "qwen_essay_result.json"
# pdf_path = work_dir / "essay_report.pdf"


# def run_list(cmd_list):
#     """使用列表执行命令，避免路径空格问题"""
#     print("==>", " ".join([str(x) for x in cmd_list]))
#     subprocess.check_call(cmd_list)


# # 1) 生成 JSON
# # run_list([
# #     sys.executable,        # 当前 Python 解释器路径（安全）
# #     "Qwen.py",
# #     "--out",
# #     str(json_path)
# # ])
# run_list([
#     sys.executable,
#     "Qwen.py",
#     "--out", str(json_path),
#     "--images",
#     r"优秀5-1.jpg",
#     r"优秀5-2.jpg"
# ])


# # 2) 构建前端
# # shell 命令改为 node/npm 可执行文件 + 参数列表
# # run_list(["npm", "run", "build"])
# run_list([r"D:\Software\nodejs\npm.cmd", "run", "build"])


# # 3) 生成 PDF
# run_list([
#     "node",
#     "export-pdf.js",
#     f"--json={json_path}",
#     f"--out={pdf_path}",
#     "--dist=./dist",
#     "--port=4173"
# ])


# # 4) 返回结果
# result = {"status": "ok", "json": str(json_path), "pdf": str(pdf_path)}
# print(json.dumps(result))
