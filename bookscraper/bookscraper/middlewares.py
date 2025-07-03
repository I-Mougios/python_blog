# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

# useful for handling different item types with a single interface
import random

import requests
from itemadapter import ItemAdapter  # noqa F401
from scrapy import signals


class ScrapeOpsUserAgentMiddleware(object):

    def process_request(self, request, spider):
        print(f"process_request method was called: {request}")
        """This is a method that scrapy will look for """
        ua = random.choice(self.user_agents_list)
        request.headers["User-Agent"] = ua

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def __init__(self, settings):
        self.scrape_ops_api_key = settings.get("SCRAPE_OPS_API_KEY")
        self.scrape_ops_endpoint = settings.get("SCRAPE_OPS_FAKE_USER_AGENT_ENDPOINT")
        self.scrape_ops_fake_user_agent_active = settings.get("SCRAPE_OPS_FAKE_USER_AGENT_ACTIVE")
        self.scrape_ops_num_results = settings.get("SCRAPE_OPS_NUM_RESULTS")
        self.headers_list = []
        self._get_user_agents_list()
        self._scrape_ops_fake_user_agents_enabled()

    def _get_user_agents_list(self):
        params = {}
        if self.scrape_ops_api_key:
            params["api_key"] = self.scrape_ops_api_key
        if self.scrape_ops_num_results:
            params["num_results"] = self.scrape_ops_num_results

        response = requests.get(self.scrape_ops_endpoint, params=params)
        result = response.json().get("result", [])
        if result:
            self.user_agents_list = result
            return

        raise KeyError("not key result in response")

    def _scrape_ops_fake_user_agents_enabled(self):
        if not self.scrape_ops_api_key or not self.scrape_ops_fake_user_agent_active:
            self.scrape_ops_fake_user_agent_active = False
        else:
            self.scrape_ops_fake_user_agent_active = True


class BookscraperSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    async def process_start(self, start):
        # Called with an async iterator over the spider start() method or the
        # maching method of an earlier spider middleware.
        async for item_or_request in start:
            yield item_or_request

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class BookscraperDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)
