def generate_url(product_url):
    if "catalogue" not in product_url:
        product_url = f"catalogue/{product_url}"

    if "https://books.toscrape.com" not in product_url:
        product_url = "https://books.toscrape.com/" + product_url
    return product_url
