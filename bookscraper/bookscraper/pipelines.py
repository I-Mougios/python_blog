# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import importlib
from decimal import Decimal
from functools import partial

import sqlalchemy as sa
from itemadapter import ItemAdapter  # noqa F401

database_package = importlib.import_module("year.2025.June.database")


def convert_star_rating(star_rating_str):
    try:
        star_rating = star_rating_str.rsplit(" ", maxsplit=1)[1].lower()
    except (IndexError, AttributeError):
        return None

    match star_rating:
        case "zero":
            return 0
        case "one":
            return 1
        case "two":
            return 2
        case "three":
            return 3
        case "four":
            return 4
        case "five":
            return 5
        case _:
            return None


class BookscraperPipeline:
    def process_item(self, item, spider):

        adapter = ItemAdapter(item)
        lowercase_keys = ["category", "product_type"]
        for key in lowercase_keys:
            value = adapter.get(key)
            adapter[key] = value.lower()

        prices_keys = ["price_excl_vat", "price_incl_vat"]
        for key in prices_keys:
            adapter[key] = Decimal(adapter.get(key, "0").strip("£"))

        availability_str = adapter.get("availability")
        availability_split = availability_str.split("(")
        try:
            number_of_pieces = availability_split[1].split(" ")[0]
        except IndexError:
            number_of_pieces = 0
        adapter["availability"] = number_of_pieces

        adapter["star_rating"] = convert_star_rating(adapter.get("star_rating"))

        int_keys = ["availability"]
        for key in int_keys:
            adapter[key] = int((adapter.get(key, 0)))

        return item


class InsertToDBPipeline:

    def __init__(
        self,
        engine: sa.Engine,
        table: sa.Table | sa.orm.DeclarativeBase,
    ):
        self.engine = engine
        self.table = table.__table__ if hasattr(table, "__table__") else table

    def process_item(self, item, spider):
        with self.engine.connect() as connection:
            try:
                connection.execute(sa.insert(self.table), parameters=item)
                connection.commit()
            except Exception:
                connection.rollback()

    def close_spider(self, spider):
        print("Closing database connection .. ")


SaveToBooksDBPipeline = partial(InsertToDBPipeline, engine=database_package.engine, table=database_package.Book)
