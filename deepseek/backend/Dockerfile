# 1. 基础镜像：Python 3.10
FROM python:3.10-slim

# 2. 设置工作目录
WORKDIR /app

# 3. 复制依赖文件
COPY requirements.txt .

# 4. 安装依赖
# --no-cache-dir 减小镜像体积
# RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
# 5. 复制所有代码
COPY . .

# 6. (可选) 默认启动命令 - 我们会在 docker-compose 里覆盖它
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]