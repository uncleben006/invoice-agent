FROM python:3.12-slim

WORKDIR /app

# 安裝系統依賴
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        python3-distutils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 安裝 Poetry
RUN pip install poetry==1.5.1

# 複製依賴檔案
COPY pyproject.toml poetry.lock* ./

# 配置 Poetry 不創建虛擬環境（在容器中不需要）
RUN poetry config virtualenvs.create false

# 安裝依賴
RUN poetry install --no-interaction --no-ansi

# 複製應用程式代碼
COPY . .

# 暴露應用埠
EXPOSE 8008

# 啟動應用
CMD ["python", "run.py"]
