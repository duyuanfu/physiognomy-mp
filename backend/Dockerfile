# 基础镜像选择稳定轻量的 Python 3.11 Slim
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Asia/Shanghai

# 安装 MediaPipe & OpenCV 必需的系统动态库 (包含 libEGL, libGL, libGLES)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libegl1 \
    libgles2 \
    libglib2.0-0 \
    libgomp1 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖清单并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 复制模型文件与后端代码
COPY face_landmarker.task .
COPY app/ ./app/
COPY .env.example .env

# 暴露端口
EXPOSE 8000

# 生产环境使用多 Worker 启动 Uvicorn，并放宽超时以保障大模型稳定响应
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--timeout-keep-alive", "75"]
