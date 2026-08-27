FROM python:3.14-slim AS base

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt


FROM base AS development

COPY requirements-dev.txt .

RUN pip install --no-cache-dir -r requirements-dev.txt


FROM base AS production

COPY app ./app
COPY alembic.ini .
COPY alembic ./alembic

RUN useradd --create-home appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]