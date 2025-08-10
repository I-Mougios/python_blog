# Python_blog
A structured, chronological catalog of:

**Library Explorations** – Focused, practical experiments with Python packages

**Utilities** – Reusable tools and scripts, often extracted from or inspired by explorations

**Mini Projects** – Goal-oriented builds combining libraries, utilities, and system integration

🧩 Code reuse across categories is encouraged: utilities may grow out of explorations, and mini-projects often use both.

### 🗂 Legend

| Symbol | Category              | Description                                                                 |
|--------|-----------------------|-----------------------------------------------------------------------------|
| 🧪     | **Library Explorations** | Hands-on experiments with specific Python libraries and tools.             |
| 🛠     | **Utilities**             | Reusable scripts, classes, or helper functions extracted from experiments. |
| 🚀     | **Mini Projects**         | End-to-end, goal-driven builds combining libraries, tools, and systems.    |

> 🧩 Utilities may originate from explorations, and mini-projects often use both.
> 
## 📅 May 2025

### 🧪 1. Decorators using `wrapt.decorator`

#### Key Takeaways
- **Closure Optimization**: `wrapt.decorator` reduces nesting vs traditional decorators
- **Runtime Control**: Enable/disable decorators via predicate functions
- **Method Support**: Handles instance/class/static methods seamlessly

### 🧪 2. Debugging with `icecream`

#### Key Takeaways
- **Debugging Efficiency**: Replace `print()` with `ic()` for automatic variable labeling
- **Execution Tracing**: Track code flow with automatic file/line number reporting
- **Production Ready**: Global toggle (`ic.disable()`) for clean production code
- **Custom Formatting**: Extend output with `argumentToString` registrations

### 🛠 3. Utility class for reading large CSV files

#### Key Features
- **Batch loading**: Reads rows in user-defined batches to avoid memory overload.
- **Dictionary output**: Each row is returned as a dictionary, just like csv.DictReader.
- **Iterator protocol**: Compatible with for loops like "for batch in reader".
- **Header flexibility**: Can infer headers or accept them explicitly.
- **Unicode robustness**: Automatically cleans and reopens files with decoding issues.
- **Smart delimiter handling**: Replaces conflicting delimiters when necessary.
- **Context manager support**: Ensures safe file handling via with blocks.

## 📅 June 2025

### 🛠 1. Dockerized SQLAlchemy + MySQL environment

> **Purpose**: Establish a robust local development environment with `SQLAlchemy`, and MySQL integration using Docker.

#### Key Highlights
- **Docker Compose** setup with two services:
  - `mysql`: A MySQL 8 container with mounted configuration and persistent storage.
  - `scrapy_db`: A Python 3.13 Alpine container that loads `.env` files and runs database logic with SQLAlchemy.
- **Environment-aware configuration**: Uses `dotenv` to load either `local.env` (outside Docker) or `mysql.env` (inside container) dynamically.
- **Test connectivity**: Includes a sample test (`tests/test_engine.py`) to validate SQLAlchemy connection.
- **Use case foundation**: This setup serves as the base for all upcoming `Scrapy` experiments.

> 📌 **Next step**: Scaffold a Scrapy project within this Dockerized structure and demonstrate DB-backed scraping pipelines.

### 🚀 2. Scrapy-powered Book Scraper

> **Purpose**: Crawl [books.toscrape.com](https://books.toscrape.com) using Scrapy, extract book metadata, and optionally store it in a MySQL database via SQLAlchemy.

---

#### 📚 Key Features

- **Pagination-aware crawling** – Supports multi-page scraping with configurable depth.
- **Modular project layout** – Separation of concerns via spiders, items, and middlewares.
- **Structured data output** – Yields a custom class that subclasses `scrapy.Item`.
- **Fake Browser-headers User-Agent support** – Simulates browser headers for more realistic requests.

---

#### ⚙️ Running the Scraper

You can run the spider either **locally** or within a **Docker container**:

---

##### 🐳 Step 1: Spin up MySQL container

```bash
  docker compose up -d mysql
```
> **📝 Note:** On first-time setup, you may need to log in as `root` and manually grant privileges to your
> application user (`i-mougios`) inside the MySQL database.


To do this, run the following commands while the MySQL container is running:

Open an interactive MySQL shell inside the container:

```docker
  docker exec -it mysql-container bash
  
  mysql -u root -p  # it will ask for your password
```
Once logged in, execute the SQL commands below to grant privileges:

```mysql
  GRANT ALL PRIVILEGES ON your_schema.* TO 'your_user'@'%' IDENTIFIED BY 'your_password'; 
  FLUSH PRIVILEGES;
```
##### Step 2: Run the Bookscraper

**Run locally**
```bash
  scrapy crawl bookspider --loglevel INFO
```

**Run inside Docker container**
```bash
  docker compose up bookscraper
```

> `docker-compose` sets:
> - working directory to src/bookscraper
> - entrypoint to scrapy
> - command as ["crawl", "bookspider", "--loglevel", "INFO"] which can be overwritten from cli


---

## 📅 July 2025

### 🧪 1.  Dicts on Steroids using `benedict` library

This notebook-style blog post explores the challenge of accessing
deeply nested dictionary data in Python using dot notation — and offers multiple robust solutions:

### Sections

- How to use `SimpleNamespace` with `json.loads(..., object_hook=...)` to support dot notation recursively.
- How to model and validate nested dictionaries using **Pydantic**, a powerful data validation library.
- How to supercharge dictionaries with **`benedict`**, a feature-rich library that:
  - Supports dot notation natively
  - Offers deep key search, flattening, filtering, matching and more

### 🎁 Bonus: Recursive Traversing and Flattening with `singledispatch`

As a bonus section, the notebook also demonstrates a clean, extensible way to **recursively flatten nested dictionaries** using Python's `functools.singledispatch`.

---
### 🛠 2. Dispatcher Utility — Dynamic Function Routing in Python

Ever wanted to replace messy `if-elif-else` trees with something cleaner and extensible?
This module introduces a reusable `Dispatcher` class, inspired by Python’s `functools.singledispatch`, that allows:

- Function dispatching based on arguments
- Flexible strategies using `key_idx`, `key_names`, and `key_generator`
- Decorator syntax for clean registration of handlers
- Method binding via descriptor protocol (supports class methods!)

#### 📁 Files Added

- `src/2025/July/dispatch.py`: The main `Dispatcher` implementation.
- `src/2025/July/dispatch_essentials.ipynb`: Notebook with hands-on examples and explanations.
- `tests/test_dispatcher.py`: Full test coverage using `pytest`, including:
  - Dispatch by string key
  - Dispatch by argument type
  - Dispatch by multiple positional/keyword arguments
  - Non-data descriptor binding (method-style dispatch)

### 🛠 3. ConfigMeta – Dynamic Configuration Loader

---
ConfigMeta is a powerful metaclass that dynamically loads configuration sections from .ini or .json files into Python classes.
Each section becomes a nested class with attributes matching the config keys.
It also provides a .get() method with support for default values and type casting.
---

📁 **Supported File Formats**
- .ini
- .json

---
📦 **Features**

- Dynamically maps each configuration section to a class-level attribute.
- Each section exposes a .get(key, default=..., cast=...) method.
>The get() method follows the resolution order: local → Globals → default.
>This means it first looks for the key in the section itself, then in the [Globals] section (if present), and finally uses the provided default.
>Supports direct attribute access (config.section.key) for keys defined in the section only.
>Globals are only visible through .get(), not as attributes.

📄 **Configuration Templates**

```json
{
  "Globals": {
    "log_level": "INFO",
    "timeout": "30"
  },
  "database": {
    "host": "localhost",
    "port": "5432",
    "loglevel": "DEBUG"
  },
  "api": {
    "endpoint": "/v1/resources",
    "token": "abc123"
  }
}
```

```ini
[Globals]
log_level = INFO
timeout = 30

[database]
host = localhost
port = 5432
log_level = DEBUG

[api]
endpoint = /v1/resources
token = abc123
```

## 📅 August 2025

---
🛠 1. DescriptorRegistry – Weakref-backed per-instance storage for descriptors
Key Takeaways
---
- Safe Per-Instance Data – Stores descriptor values without polluting __dict__ or risking recursion.

- Slots Compatibility – Works with __slots__ classes that include __weakref__.

- Automatic Cleanup – Weak reference callbacks remove data when instances are garbage collected.

- Dict-Like API – __getitem__, __setitem__, keys(), values(), items() for easy use.

- Testing – Verified with normal, slotted, and weakref-enabled classes.