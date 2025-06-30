import scrapy
from bookscraper import BookItem


class BookspiderSpider(scrapy.Spider):
    name = "bookspider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response):
        books = response.css("article.product_pod")
        for book in books:
            book_url = response.urljoin(book.css("a::attr(href)").get())
            yield response.follow(book_url, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()

        if next_page:
            next_page_url = response.urljoin(next_page)
            yield response.follow(next_page_url, callback=self.parse)

    def parse_book(self, response):
        table_rows = response.css("table tr")

        url = response.url
        title = response.css("h1::text").get()
        category = response.xpath("/html/body/div/div/ul/li[3]/a/text()").get()
        stars = response.css("p.star-rating::attr(class)").get()
        upc = table_rows[0].css("td::text").get()
        product_type = table_rows[1].css("td::text").get()
        price_excl_vat = table_rows[2].css("td::text").get()
        price_incl_vat = table_rows[3].css("td::text").get()
        availability = table_rows[5].css("td::text").get()
        n_reviews = table_rows[6].css("td::text").get()
        book_item = BookItem(
            url=url,
            title=title,
            upc=upc,
            category=category,
            star_rating=stars,
            product_type=product_type,
            price_excl_vat=price_excl_vat,
            price_incl_vat=price_incl_vat,
            availability=availability,
            n_reviews=n_reviews,
        )
        yield book_item
