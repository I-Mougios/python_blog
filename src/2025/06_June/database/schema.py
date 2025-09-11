# python_blog/src/2025/06_June/database/schema.py
from sqlalchemy import Column, Float, Integer, String, Text
from sqlalchemy.orm import mapped_column

from .base import Base, engine


class Book(Base):
    __tablename__ = "books"

    _id = mapped_column("id", Integer, primary_key=True, autoincrement=True)
    upc = Column(String(50), primary_key=True)
    url = Column(Text, nullable=False)
    title = Column(String(255), nullable=False)
    category = Column(String(100))
    star_rating = Column(Integer)
    product_type = Column(String(50))
    price_excl_vat = Column(Float)
    price_incl_vat = Column(Float)
    availability = Column(String(100))
    n_reviews = Column(Integer)


Book.__table__.drop(engine, checkfirst=True)
Base.metadata.create_all(engine, checkfirst=True)
