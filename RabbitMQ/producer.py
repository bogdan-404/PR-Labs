import requests
from bs4 import BeautifulSoup
import pika


def setup_rabbitmq():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
    channel = connection.channel()
    channel.queue_declare(queue="url_queue")
    return connection, channel


def send_url_to_queue(channel, url):
    channel.basic_publish(exchange="", routing_key="url_queue", body=url)


def recursive(maxIterations, currentIteration, URL_array, channel):
    if currentIteration >= maxIterations or currentIteration >= len(URL_array):
        return

    URL = URL_array[currentIteration]
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")

    for link in soup.find_all("a", href=True, class_="js-item-ad"):
        href = link.get("href")
        if href and href[1] != "b":
            url_to_append = "https://999.md" + href
            send_url_to_queue(channel, url_to_append)

    pages = soup.select("nav.paginator > ul > li > a")
    for page in pages:
        href = page.get("href")
        if href:
            link = "https://999.md" + href
            if link not in URL_array:
                URL_array.append(link)

    recursive(maxIterations, currentIteration + 1, URL_array, channel)


if __name__ == "__main__":
    URL_array = ["https://999.md/ro/list/transport/cars"]
    connection, channel = setup_rabbitmq()
    try:
        recursive(1000000, 0, URL_array, channel)
    finally:
        connection.close()
