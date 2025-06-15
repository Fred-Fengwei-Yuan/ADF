FROM python:3.11-slim


WORKDIR /code


COPY ./requirements.txt /code/requirements.txt


RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*


RUN curl -LsSf https://astral.sh/uv/install.sh | sh


RUN uv sync --no-dev


COPY ./app /code/app


CMD ["fastapi", "run", "app/main.py", "--port", "80", "--host", "0.0.0.0", "--workers", "4"]