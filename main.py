import os
import uuid
import shutil
from typing import List
import json
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from celery import chain
from celery.result import AsyncResult
from tasks import grade_essay_multipage, generate_pdf_report
from celery_utils import celery_app

app = FastAPI(title="作文批改 API", description="使用 Celery 和 Qwen-VL-Max 进行异步作文批改")

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.post("/grade_essay", status_code=202, summary="提交批改任务链")
def submit_grading_task(
    images: List[UploadFile] = File(..., description="作文图片文件列表"), 
    prompt: str = Form("这是学生写的作文...", description="给模型的提示词")
):
    if not images:
        raise HTTPException(status_code=400, detail="没有提供任何图片文件。")

    image_paths = []
    request_id = str(uuid.uuid4())
    request_upload_dir = os.path.join(UPLOAD_FOLDER, request_id)
    os.makedirs(request_upload_dir)

    try:
        for image in images:
            filepath = os.path.join(request_upload_dir, image.filename)
            with open(filepath, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
            image_paths.append(filepath)
    finally:
        for image in images:
            image.file.close()

    if not image_paths:
        raise HTTPException(status_code=500, detail="未能成功保存任何上传的图片。")

    # --- 创建并启动任务链 ---
    # 1. 定义第一个任务的签名 (Signature)
    grading_task_signature = grade_essay_multipage.s(image_path_list=image_paths, prompt_text=prompt)
    
    # 2. 定义第二个任务的签名
    # 注意：这里我们不需要为它的第一个参数传值，Celery会自动将上一个任务的结果传入
    pdf_task_signature = generate_pdf_report.s()

    # 3. 将两个任务链接成一个链条
    task_chain = chain(grading_task_signature, pdf_task_signature)

    # 4. 异步执行任务链
    chain_result = task_chain.apply_async()

    # 返回整个链条的 ID
    return {"task_id": chain_result.id}


@app.get("/result/{task_id}", summary="查询任务链结果")
def get_task_result(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)

    response = {
        'task_id': task_id,
        'status': task_result.status,
        'result': None
    }

    if task_result.successful():
        # 当任务链成功时，获取最终任务（PDF生成）的结果
        response['result'] = task_result.get()
            
    elif task_result.failed():
        response['result'] = str(task_result.info)

    return JSONResponse(content=response)
