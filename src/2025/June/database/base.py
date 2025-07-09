# python_blog/src/2025/June/database/base.py
import os
from pathlib import Path

import sqlalchemy as sa
from dotenv import load_dotenv
from sqlalchemy.orm import DeclarativeBase

__all__ = ["engine", "Base"]

# Points to # python_blog/src/2025/June/database
base_dir = Path(__file__).resolve().parents[0]


# Detect if running inside a Docker container
def running_inside_docker():
    return Path("/.dockerenv").exists()


if running_inside_docker():
    # Load container configs first if exist from the bind mount
    load_dotenv(base_dir / "mysql.env", override=True)
else:
    # Load local dev configs first
    load_dotenv(base_dir / "local.env", override=True)


db_username = os.getenv("MYSQL_USER")
db_password = os.getenv("MYSQL_PASSWORD")
db_name = os.getenv("MYSQL_DATABASE")
db_host = os.getenv("MYSQL_HOST", "localhost")
db_port = int(os.getenv("MYSQL_PORT", 3306))
echo = os.getenv("MYSQL_ECHO", False)

mysql_uri = f"mysql+pymysql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}"
engine = sa.create_engine(mysql_uri, echo=echo)


class Base(DeclarativeBase):
    """Parent class of all SQL tables"""
