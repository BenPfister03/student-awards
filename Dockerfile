# syntax=docker/dockerfile:1
FROM python:3.12-slim

WORKDIR /app

COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app
COPY ./manage.py ./
COPY ./vendor ./vendor
COPY ./.env.example ./

ENV PYTHONUNBUFFERED=1
EXPOSE 8000

CMD ["python", "manage.py", "run", "--host", "0.0.0.0", "--port", "8000"]
