import requests
from bs4 import BeautifulSoup
import pika
from tinydb import TinyDB

db = TinyDB("db.json")


def extract_info(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    dict_result = {}

    title = soup.find("h1", itemprop="name")
    if title:
        dict_result["Title"] = title.text.strip()

    price = soup.find(
        "span", class_="adPage__content__price-feature__prices__price__value"
    )
    currency = soup.find("span", itemprop="priceCurrency")
    if price and currency:
        dict_result["Price"] = (
            price.text.strip() + " " + currency.get("content", "").strip()
        )

    location = soup.find("strong", class_="adPage__content__region")
    if location:
        dict_result["Location"] = location.text.strip()

    dict_result["URL"] = url

    desc = soup.find("div", itemprop="description")
    if desc:
        dict_result["Description"] = desc.text.strip()

    return dict_result


def callback(ch, method, properties, body):
    url = body.decode()
    print(f"Processing URL: {url}")
    try:
        data = extract_info(url)
        db.insert(data)
        print(f"Data inserted for URL: {url}")
    except Exception as e:
        print(f"Failed to process URL {url}: {e}")
    finally:
        ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
    channel = connection.channel()
    channel.queue_declare(queue="url_queue")

    channel.basic_consume(
        queue="url_queue", on_message_callback=callback, auto_ack=False
    )
    print(" [*] Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()


if __name__ == "__main__":
    main()
