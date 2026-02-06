## 1) Development: запуск застосунку окремо


main.py запускається тільки як 
`python -m app.main` 

або 

`uvicorn app.main:app --reload`


### Run with Docker Compose (Postgres 16 + API)

### Prerequisites
- Docker Desktop (Windows/macOS) or Docker Engine (Linux)
- `docker compose` доступний у терміналі

## 2) Configure environment
Проєкт використовує файл `.env.docker` для Docker-середовища.

Переконайтесь, що в `.env.docker` виставлені (мінімум) такі змінні:

```env
# Postgres container config
POSTGRES_DB=photoshare
POSTGRES_USER=photoshare
POSTGRES_PASSWORD=photoshare

# Host port mapping (your machine -> container)
POSTGRES_HOST_PORT=5432

# App DB connection (container -> container)
DB_HOST=db
DB_PORT=5432
DB_USER=photoshare
DB_PASSWORD=photoshare
DB_NAME=photoshare

# Auth (dev)
SECRET_KEY=dev-secret-change-me
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# App port (your machine -> container)
APP_HOST_PORT=8000
```
Note: DB_PORT всередині Docker мережі має бути 5432.
Якщо у вас вже зайнятий порт 5432 на хості — змініть тільки POSTGRES_HOST_PORT, наприклад на 15432.

## 3) Build & start

Запуск з кореня репозиторію:

`docker compose --env-file .env.docker up --build`


Щоб запустити в фоні:

`docker compose --env-file .env.docker up --build -d`


Зупинити:

docker compose down
## 4) Open the application

Swagger UI: http://127.0.0.1:8000/docs

OpenAPI JSON: http://127.0.0.1:8000/openapi.json

Не використовуйте http://0.0.0.0:8000 у браузері — 0.0.0.0 це адреса для bind (слухати на всіх інтерфейсах), а не адреса для відкриття сторінки.
