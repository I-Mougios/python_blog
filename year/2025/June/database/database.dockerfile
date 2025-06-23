FROM python:3.13-alpine

# Install build dependencies required for some Python packages (e.g., cryptography)
RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev

# Set working directory inside container
WORKDIR /database

# Copy the relevant code into the container
COPY . /database

# Create virtual environment
RUN python -m venv .venv

# Activate venv and install dependencies
# Alpine shell uses `sh`, not `bash`, so we call pip directly
RUN .venv/bin/pip install --no-cache-dir python-dotenv sqlalchemy pymysql cryptography icecream

# Create an anonymous volume to avoid overwrite .venv from any bind mount
VOLUME ["/database/.venv"]

# Default command to run
ENTRYPOINT [".venv/bin/python"]