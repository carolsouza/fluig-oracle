import scrapy
from scraper.items import ScraperItem


class FluigDevSpider(scrapy.Spider):
    name = "fluig_dev_spider"
    allowed_domains = ["style.fluig.com"]
    start_urls = ["https://style.fluig.com/"]

    def parse(self, response):
        # Percorre o menu principal
        for main_menu_item in response.css("ul.nav.navbar-nav.navbar-left.nav-main-menu li"): 
            category = main_menu_item.css("a::text").get()
            category_url = main_menu_item.css("a::attr(href)").get()
            if category_url:
                yield response.follow(
                    category_url,
                    callback=self.parse_side_menu,
                    meta={'category': category}
                )

    def parse_side_menu(self, response):
        category = response.meta['category']
        # Percorre o menu lateral
        for nav_item in response.css("ul.fluig-docs-list-category.list-unstyled.nav li"):
            title = nav_item.css("a::text").get()
            url = nav_item.css("a::attr(href)").get()
            if url:
                yield response.follow(
                    url,
                    callback=self.parse_content,
                    meta={'category': category, 'title': title, 'url': response.urljoin(url)}
                )

    def parse_content(self, response):
        content = ScraperItem()
        content["category"] = response.meta['category']
        content["title"] = response.meta['title']
        content["url"] = response.meta['url']
        content["content"] = response.css("div.content__main").get()
        yield content
        
        