import scrapy
import logging

from bookstoscrape.helpers.generate_url import generate_url
from bookstoscrape.items import BookstoscrapeItem

logging.basicConfig(
    # level=logging.INFO,
    filename="books_to_scrape.log"
)
logger = logging.getLogger(__name__)


class GetProductsSpider(scrapy.Spider):
    name = "get_products"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    def parse(self, response):
        # fetch all product links
        product_links = response.css(
            "div.col-sm-8.col-md-9 section div ol.row li.col-xs-6.col-sm-4.col-md-3.col-lg-3 article.product_pod h3 a::attr(href)"
        ).extract()
        logger.info({"product_links": product_links, "len": len(product_links)})

        # load product page
        for index, product_link in enumerate(product_links):
            logger.info({f"product_link {index}": generate_url(product_link)})
            yield scrapy.Request(
                url=generate_url(product_link), callback=self.parse_product
            )

        # check for next page and load next page
        next_page = response.css("ul.pager li.next a::attr(href)").extract_first()
        if next_page:
            yield scrapy.Request(url=generate_url(next_page), callback=self.parse)

    def parse_product(self, response):
        product = BookstoscrapeItem()
        product["title"] = response.css("h1::text").extract_first()
        product["image"] = (
            response.css("div.item.active img::attr(src)")
            .extract_first()
            .replace("../../", "")
        )
        product["description"] = response.xpath("//p[not(@class)]/text()").get()
        product["breadcrumb"] = " >> ".join(
            response.css("ul.breadcrumb li a::text").extract()
        )

        product_information = response.css("table.table.table-striped")

        product["upc"] = product_information.xpath(
            "//tr/th[text()='UPC']/following-sibling::td/text()"
        ).extract_first()
        product["product_type"] = product_information.xpath(
            "//tr/th[text()='Product Type']/following-sibling::td/text()"
        ).extract_first()
        product["price_excl_tax"] = product_information.xpath(
            "//tr/th[text()='Price (excl. tax)']/following-sibling::td/text()"
        ).extract_first()
        product["price_incl_tax"] = product_information.xpath(
            "//tr/th[text()='Price (incl. tax)']/following-sibling::td/text()"
        ).extract_first()
        product["tax"] = product_information.xpath(
            "//tr/th[text()='Tax']/following-sibling::td/text()"
        ).extract_first()
        product["inventory"] = product_information.xpath(
            "//tr/th[text()='Availability']/following-sibling::td/text()"
        ).extract_first()
        product["no_of_reviews"] = product_information.xpath(
            "//tr/th[text()='Number of reviews']/following-sibling::td/text()"
        ).extract_first()

        yield product
