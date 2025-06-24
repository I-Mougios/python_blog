import scrapy
from icecream import ic


class BookspiderSpider(scrapy.Spider):
    name = "bookspider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response):
        books = response.css("article.product_pod")
        for book in books:
            yield {
                "title": book.css("h3 a::attr(title)").get(),
                "price": book.css("div.product_price p.price_color::text").get(),
                "url": book.css("h3 a").attrib["href"],
            }

        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            full_url = ic(response.urljoin(next_page))
            yield response.follow(full_url, callback=self.parse)
