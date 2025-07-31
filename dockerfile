FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY poetry.lock pyproject.toml /app/
RUN pip install poetry && poetry config virtualenvs.create false && poetry install --no-dev
COPY EasyTask /app/EasyTask
COPY docker /app/docker
CMD ["gunicorn", "EasyTask.wsgi:application", "--bind", "0.0.0.0:8000"]