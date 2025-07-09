FROM python:3.13-alpine

RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev

WORKDIR /app

COPY src/bookscraper /app/src/bookscraper
COPY src/2025/June/database /app/src/2025/June/database

RUN pip install --no-cache-dir python-dotenv sqlalchemy pymysql cryptography icecream scrapy brotli brotlicffi

ENV PYTHONPATH=/app/src