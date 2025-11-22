from celery import Celery
import os
from dotenv import load_dotenv
from .service import chat_with_deepseek

load_dotenv()

# 1. 定义 Celery 应用
# broker: 任务队列在哪里？ (Redis)
# backend: 结果存哪里？ (Redis)
celery_app = Celery(
    "worker",
    broker=os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")
)

# 2. 定义任务 (Task)
# 加上 @celery_app.task 装饰器，这个函数就变成了可以异步执行的任务
@celery_app.task(name="chat_task")
def chat_task(messages):
    print(f"🍳 厨师开始炒菜: {messages}")
    try:
        reply = chat_with_deepseek(messages)
        print(f"✅ 菜做好了: {reply[:20]}...")
        return reply
    except Exception as e:
        print(f"🔥 炸厨房了: {e}")
        return str(e)