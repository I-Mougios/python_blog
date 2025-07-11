FROM python:3.13-alpine

WORKDIR app

COPY src/bookstore_api/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/app/src

EXPOSE 8000