# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BookItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    category = scrapy.Field()
    stars = scrapy.Field()
    product_type = scrapy.Field()
    price_excl_vat = scrapy.Field()
    price_incl_vat = scrapy.Field()
    availability = scrapy.Field()
    n_reviews = scrapy.Field()
    upc = scrapy.Field()
