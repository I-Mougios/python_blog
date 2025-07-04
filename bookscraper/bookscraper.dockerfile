FROM python:3.13-alpine

# Install build dependencies required for some Python packages (e.g., cryptography)
RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev

WORKDIR /app
COPY bookscraper /app/bookscraper
COPY year/2025/June/database /app/year/2025/June/database

RUN pip install --no-cache-dir python-dotenv sqlalchemy pymysql cryptography icecream scrapy brotli brotlicffi

ENV PYTHONPATH=/app

ENTRYPOINT ["sh", "-c", "cd bookscraper && exec scrapy crawl \"$@\"", "--"]