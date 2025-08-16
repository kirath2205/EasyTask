FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app
# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*
COPY poetry.lock pyproject.toml /app/
RUN pip install poetry && poetry config virtualenvs.create false && poetry install
COPY EasyTask /app/EasyTask
COPY docker /app/docker
WORKDIR /app/EasyTask
CMD ["gunicorn", "EasyTask.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "8"]