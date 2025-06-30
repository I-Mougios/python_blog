# Python_blog
A structured catalog of Python library explorations, custom utilities, and mini-projects organized chronologically.

## 📅 May 2025

### 1. Decorators using `wrapt.decorator`

#### Key Takeaways
- **Closure Optimization**: `wrapt.decorator` reduces nesting vs traditional decorators
- **Runtime Control**: Enable/disable decorators via predicate functions
- **Method Support**: Handles instance/class/static methods seamlessly

### 2. Debugging with `icecream`

#### Key Takeaways
- **Debugging Efficiency**: Replace `print()` with `ic()` for automatic variable labeling
- **Execution Tracing**: Track code flow with automatic file/line number reporting
- **Production Ready**: Global toggle (`ic.disable()`) for clean production code
- **Custom Formatting**: Extend output with `argumentToString` registrations

### 3. Utility class for reading large CSV files

#### Key Features
- **Batch loading**: Reads rows in user-defined batches to avoid memory overload.
- **Dictionary output**: Each row is returned as a dictionary, just like csv.DictReader.
- **Iterator protocol**: Compatible with for loops like "for batch in reader".
- **Header flexibility**: Can infer headers or accept them explicitly.
- **Unicode robustness**: Automatically cleans and reopens files with decoding issues.
- **Smart delimiter handling**: Replaces conflicting delimiters when necessary.
- **Context manager support**: Ensures safe file handling via with blocks.

## 📅 June 2025

### 1. Dockerized SQLAlchemy + MySQL environment

> **Purpose**: Establish a robust local development environment with `SQLAlchemy`, and MySQL integration using Docker.

#### Key Highlights
- **Docker Compose** setup with two services:
  - `mysql`: A MySQL 8 container with mounted configuration and persistent storage.
  - `scrapy_db`: A Python 3.13 Alpine container that loads `.env` files and runs database logic with SQLAlchemy.
- **Environment-aware configuration**: Uses `dotenv` to load either `local.env` (outside Docker) or `mysql.env` (inside container) dynamically.
- **Test connectivity**: Includes a sample test (`tests/test_engine.py`) to validate SQLAlchemy connection.
- **Use case foundation**: This setup serves as the base for all upcoming `Scrapy` experiments.

> 📌 **Next step**: Scaffold a Scrapy project within this Dockerized structure and demonstrate DB-backed scraping pipelines.
