from celery import Celery

# 使用 Redis 作为消息代理和结果后端
# 你需要确保本地或服务器上已经安装并运行了 Redis
# 默认连接到 redis://127.0.0.1:6379/0
celery_app = Celery(
    'tasks',
    broker='redis://127.0.0.1:6379/0',
    backend='redis://127.0.0.1:6379/0',
    include=['tasks']
)

# 可选配置
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Shanghai',
    enable_utc=True,
)

