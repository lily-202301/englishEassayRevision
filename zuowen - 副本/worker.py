import os
import sys
import subprocess
import json
from celery import Celery

# 1. 配置 Celery (连接本地 Redis)
celery_app = Celery(
    "essay_worker",
    broker="redis://127.0.0.1:6379/0",
    backend="redis://127.0.0.1:6379/1"
)

# 2. 定义任务
@celery_app.task(name="grade_essay_task")
def grade_essay_task(image_paths: list, task_id: str):
    """
    参数:
    - image_paths: 图片的绝对路径列表
    - task_id: 任务ID (用于生成独立的输出文件夹)
    """
    
    # --- A. 准备输出路径 ---
    # 为了避免并发冲突，每个任务必须有独立的输出文件
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_dir, "runs", task_id)
    os.makedirs(output_dir, exist_ok=True)
    
    json_path = os.path.join(output_dir, "result.json")
    pdf_path = os.path.join(output_dir, "report.pdf")
    
    print(f"🔥 [Worker] 开始处理任务 {task_id}")
    print(f"📂 输出目录: {output_dir}")

    try:
        # --- B. 调用 Qwen.py (大模型批改) ---
        # 相当于在命令行执行: python Qwen.py --images "img1" "img2" --out "result.json"
        
        # 构造命令行参数
        qwen_cmd = [
            sys.executable,  # 当前 python 解释器路径
            "Qwen.py",
            "--out", json_path,
            "--images"
        ] + image_paths # 把图片列表加进去

        print(f"✨ 执行 Qwen: {' '.join(qwen_cmd)}")
        subprocess.check_call(qwen_cmd, cwd=base_dir) # cwd确保在根目录运行

        # --- C. 调用 export-pdf.js (生成PDF) ---
        # 假设你的 node 环境已配好
        # node export-pdf.js --json=... --out=...
        node_cmd = [
            "node", 
            "export-pdf.js",
            f"--json={json_path}",
            f"--out={pdf_path}",
            "--dist=./dist", # 你的前端资源目录
            "--port=4173"
        ]
        
        print(f"✨ 执行 Node PDF: {' '.join(node_cmd)}")
        # 注意：这里需要 shell=True (Windows下调用node可能需要)
        subprocess.check_call(node_cmd, cwd=base_dir, shell=True)

        # --- D. 读取结果并返回 ---
        # 读取 Qwen 生成的 JSON 内容返回给前端显示
        with open(json_path, "r", encoding="utf-8") as f:
            analysis_result = json.load(f)

        return {
            "status": "success",
            "score": analysis_result.get("overall_evaluation", {}).get("total_score", 0),
            "pdf_path": pdf_path,   # 绝对路径
            "json_path": json_path, # 绝对路径
            "analysis": analysis_result
        }

    except subprocess.CalledProcessError as e:
        # 如果 Qwen.py 或 Node 报错
        return {"status": "error", "message": f"Subprocess failed: {str(e)}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}