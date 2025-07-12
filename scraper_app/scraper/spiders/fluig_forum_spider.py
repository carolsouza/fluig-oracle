import scrapy
from scraper.items import ScraperItem
from markdownify import markdownify as md


class FluigForumSpider(scrapy.Spider):
    name = "fluig_forum_spider"
    allowed_domains = ["fluiggers.com.br"]
    start_urls = ["https://fluiggers.com.br/"]

    def parse(self, response):
        categories = response.css("table.category-list tbody tr")

        for main_category in categories:
            category = main_category.css("td.category h3 span::text").get()
            category_url = main_category.css("td.category h3 a::attr(href)").get()

            print(f"category: {category} - category_url: {category_url}")

            if category_url:
                yield response.follow(
                    category_url,
                    callback=self.parse_category_subjects,
                    meta={"category": category},
                )

    def parse_category_subjects(self, response):
        subjects = response.css("tbody tr.topic-list-item")

        for category_subjects in subjects:
            subject_url = category_subjects.css(
                "td.main-link span a.raw-topic-link::attr(href)"
            ).get()

            if subject_url:
                yield response.follow(
                    subject_url,
                    callback=self.parse_subjects_content,
                    meta={"category": response.meta["category"]},
                )

    def parse_subjects_content(self, response):
        content = ScraperItem()

        content["url"] = response.url
        content["category"] = response.meta["category"]
        content["title"] = response.css("div#topic-title a::text").get()
        content["content"] = response.css("div.post-stream::text").get()

        md_content = md(
            response.css("div.post-stream").get(), strip=["a", "img", "script", "style", "input"]
        )
        
        content["content_md"] = md_content 
        
        yield content
