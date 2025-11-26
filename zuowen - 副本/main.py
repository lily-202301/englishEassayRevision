from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from celery.result import AsyncResult
import shutil
import os
import uuid
from typing import List
from worker import celery_app, grade_essay_task # 导入刚才写的 worker

app = FastAPI()

# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 确保上传目录存在
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/submit")
async def submit_essay(files: List[UploadFile] = File(...)):
    """
    1. 接收多张图片
    2. 存到本地 uploads 文件夹
    3. 触发 Celery 任务
    """
    task_id = str(uuid.uuid4()) # 生成唯一任务ID
    saved_paths = []
    
    # 1. 保存图片
    for file in files:
        # 为了防止文件名冲突，加个前缀
        safe_filename = f"{task_id}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, safe_filename)
        absolute_path = os.path.abspath(file_path)
        
        with open(absolute_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        saved_paths.append(absolute_path)
    
    # 2. 发送任务给 Worker (异步!)
    # delay() 是 Celery 的精髓，它会立刻返回，不会卡顿
    task = grade_essay_task.delay(saved_paths, task_id)
    
    return {
        "task_id": task.id, 
        "message": "已进入批改队列",
        "image_count": len(saved_paths)
    }

@app.get("/status/{task_id}")
def get_status(task_id: str):
    """
    前端轮询此接口获取进度
    """
    task_result = AsyncResult(task_id, app=celery_app)
    
    if task_result.state == 'PENDING':
        return {"status": "Queued", "progress": 0}
    elif task_result.state == 'STARTED':
        return {"status": "Processing", "progress": 50}
    elif task_result.state == 'SUCCESS':
        return {"status": "Completed", "progress": 100, "result": task_result.result}
    elif task_result.state == 'FAILURE':
        return {"status": "Failed", "error": str(task_result.info)}
    
    return {"status": task_result.state}