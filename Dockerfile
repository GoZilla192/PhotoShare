FROM python:3.12-slim

WORKDIR /app

# system deps (мінімум)
RUN pip install --no-cache-dir poetry

# встановлюємо залежності окремим шаром (швидше rebuild)
COPY pyproject.toml poetry.lock* README.md /app/
RUN poetry config virtualenvs.create false \
 && poetry install --no-interaction --no-ansi  --no-root

# копіюємо код
COPY . /app

EXPOSE 8000