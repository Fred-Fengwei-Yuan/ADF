FROM python:3.11-slim


WORKDIR /app


RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*


COPY pyproject.toml uv.lock ./


RUN pip install uv


RUN uv sync --frozen


COPY . .


RUN mkdir -p logs


EXPOSE 8000


ENV PYTHONPATH=/app
ENV API_WORKERS=4
ENV ENGINE_WORKERS=2
ENV TASK_QUEUE_SIZE=1000


CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]