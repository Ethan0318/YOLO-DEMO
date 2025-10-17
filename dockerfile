FROM python:3.11

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

# 更新GPG密钥并安装系统依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends --allow-unauthenticated \
    libgl1 \
    libglib2.0-0 \
    ffmpeg && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app/static/uploads

EXPOSE 5000

# 设置环境变量
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# 启动命令
CMD ["gunicorn","--bind","0.0.0.0:5000","app:app"]