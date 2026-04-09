FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY pyproject.toml README.md /app/
COPY apps /app/apps
COPY packages /app/packages
COPY temporal /app/temporal
RUN pip install --upgrade pip && pip install -e .

COPY . /app

CMD ["uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
