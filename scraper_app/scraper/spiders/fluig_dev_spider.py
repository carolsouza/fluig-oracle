import scrapy
from scraper.items import ScraperItem
from markdownify import markdownify as md
import re

class FluigDevSpider(scrapy.Spider):
    name = "fluig_dev_spider"
    allowed_domains = ["style.fluig.com"]
    start_urls = ["https://style.fluig.com/"]

    # This spider scrapes the Fluig Dev documentation site
    # It extracts the main menu items and their corresponding side menu content
    def parse(self, response):
        for main_menu_item in response.css(
            "ul.nav.navbar-nav.navbar-left.nav-main-menu li"
        ):
            category = main_menu_item.css("a::text").get()
            category_url = main_menu_item.css("a::attr(href)").get()
            if category_url:
                yield response.follow(
                    category_url,
                    callback=self.parse_side_menu,
                    meta={"category": category},
                )

    def parse_side_menu(self, response):
        print(f"parse_side_menu: {response.url}")

        category = response.meta["category"]
        for nav_item in response.css("div.bs-docs-section"):
            title = (
                nav_item.css("h1.page-header::text").get()
                or nav_item.css("h1::text").get()
            )

            content = ScraperItem()
            content["category"] = category
            content["title"] = title
            content["url"] = response.url
            content["content"] = nav_item.get()
            md_content = md(
                nav_item.get(), strip=["a", "img", "script", "style", "input"]
            )

            # Remove images and {{...}} from the markdown content
            md_content = "\n".join(
                line
                for line in md_content.splitlines()
                if "<img" not in line and not re.search(r"\{\{.*?\}\}", line)
            )
            
            content["content_md"] = md_content

            yield content
