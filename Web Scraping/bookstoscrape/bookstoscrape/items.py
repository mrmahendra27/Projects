# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BookstoscrapeItem(scrapy.Item):
    title = scrapy.Field()
    image = scrapy.Field()
    upc = scrapy.Field()
    product_type = scrapy.Field()
    price_excl_tax = scrapy.Field()
    price_incl_tax = scrapy.Field()
    tax = scrapy.Field()
    inventory = scrapy.Field()
    no_of_reviews = scrapy.Field()
    breadcrumb = scrapy.Field()
    description = scrapy.Field()
