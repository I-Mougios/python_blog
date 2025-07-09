import importlib
import time

import sqlalchemy as sa

base_module = importlib.import_module("src.2025.June.database.base")
engine = base_module.engine


def test_engine():
    time.sleep(2)
    with engine.connect() as connection:
        connection.execute(sa.text("SELECT 1 FROM DUAL"))
