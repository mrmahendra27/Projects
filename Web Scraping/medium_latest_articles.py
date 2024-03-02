import requests
import smtplib
import os
import pandas as pd
import datetime
import logging

from lxml import html
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

file_path = "medium_latest_articles.xlsx"
topic = "Artificial Intelligence"
website_url = "https://medium.com/"
website_name = "Medium"

logging.basicConfig(
    filename="medium_latest_articles.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


def convert_and_store_data(article_lists: list):
    df = pd.DataFrame(data=article_lists)
    df.to_excel(
        file_path,
        index=False,
    )

    logger.info("Data converted and stored in Excel")


def send_mail(article_lists: list):
    port = 2525
    smtp_server = "sandbox.smtp.mailtrap.io"
    username = "b256ab85edee9c"
    password = "e51d04fea2c193"

    today = datetime.datetime.now()
    date = today.strftime("%d-%m-%Y")
    day_of_week = today.strftime("%A")

    subject = f"Latest Articles on {topic} for {date}"
    sender_email = "mailtrap@example.com"
    receiver_email = "new@example.com"

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    # Add body to email
    html_body = f"""
    <html>
    <body>
        <p>Hi Mahendra,</p>
        <p>Happy {day_of_week}! ☀️</p>
        <p>This is our daily update with some of the latest and most interesting articles on <b>{topic}</b> from <a href="{website_url}">{website_name}</a></p>
        <ul>
    """

    for article_list in article_lists:
        html_body += f"""<li><a href="{article_list["Link"]}">{article_list["Title"]}</a>: {article_list["Title"]}</li>"""

    html_body += f"""
        </ul>
        
        <p>The attachment with the article details has been attached below.</p>
        <p>We hope you enjoy reading these articles!</p>
        <p>Have a great day!</p>
        <p>Best regards,</p>
        <p>The Team at Scraper</p>
    </body>
    </html>
    """
    message.attach(MIMEText(html_body, "html"))

    # We assume that the file is in the directory where you run your Python script from
    with open(file_path, "rb") as attachment:
        # The content type "application/octet-stream" means that a MIME attachment is a binary file
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    # Encode to base64
    encoders.encode_base64(part)

    # Add header
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {file_path}",
    )

    # Add attachment to your message and convert it to string
    message.attach(part)
    text = message.as_string()

    # send your email
    with smtplib.SMTP(smtp_server, port) as server:
        server.login(username, password)
        server.sendmail(sender_email, receiver_email, text)

    logger.info("Mail Sent Successfully!")


def scrap_latest_articles(url: str, headers: dict):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for non-200 status codes

        article_lists = []
        website_url = "https://medium.com"
        if response.status_code == 200:
            data = html.fromstring(response.content)

            articles = data.xpath(
                "//div[@class='jb jc jd je jf l']/div/div[@class='ku kv kw l']/div/article/div/div/div/div"
            )
            for article in articles:
                author_name = article.xpath(
                    ".//div[1]/div[2]/div[1]/div[1]/a[1]/p[1]/text()"
                )[0]

                author_profile = article.xpath(
                    ".//div[1]/div[2]/div[1]/div[1]/a[1]/@href"
                )[0]

                article_title = article.xpath(".//div[2]/div[1]/a[1]/h2[1]/text()")[0]

                article_link = article.xpath(".//div[2]/div[1]/a[1]/@href")[0]

                image = article.xpath(".//div[2]/div[2]/a[1]/div[1]/img[1]/@src")
                article_image = image[0] if image else ""

                article_likes = article.xpath(
                    ".//div[3]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/p[1]/button[1]/text()"
                )

                article_lists.append(
                    {
                        "Title": article_title,
                        "Link": f"{website_url}{article_link}",
                        "Image": article_image,
                        "Author Name": author_name,
                        "Author Profile": f"{website_url}{author_profile}",
                        "Likes": article_likes,
                    }
                )

            if article_lists:
                convert_and_store_data(article_lists)

                if os.path.exists(file_path):
                    send_mail(article_lists)
                    logger.info("Process Completed")
    except Exception as e:
        logger.error({"Error": e})


if __name__ == "__main__":
    url = "https://medium.com/tag/artificial-intelligence/archive"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    scrap_latest_articles(url, headers)
