import socket
import re
from bs4 import BeautifulSoup

HOST = '127.0.0.1'
PORT = 8080


def send_request(path):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT))
        request = f"GET {path} HTTP/1.1\r\nHost: {HOST}\r\n\r\n"
        client_socket.sendall(request.encode('utf-8'))
        response = client_socket.recv(4096).decode('utf-8')
        return response


def parse_response(response):
    # Check if the response has the expected format
    if "\r\n\r\n" not in response:
        print("Unexpected response format:")
        print(response)
        return ""

    # Extract the content from the HTTP response
    content = response.split("\r\n\r\n", 1)[1]

    # Use BeautifulSoup to parse the HTML content
    soup = BeautifulSoup(content, 'html.parser')

    # If it's a product page, extract the product details
    if "/shop/" in response:
        details = {}
        details['Title'] = soup.find(
            'li', text=re.compile('Title:')).text.split(': ')[1]
        details['Author'] = soup.find(
            'li', text=re.compile('Author:')).text.split(': ')[1]
        details['Price'] = float(
            soup.find('li', text=re.compile('Price:')).text.split(': ')[1])
        details['Small Description'] = soup.find(
            'li', text=re.compile('Small Description:')).text.split(': ')[1]
        return details
    else:
        return content


# Fetch the shop page and extract product links
shop_response = send_request("/shop")
shop_soup = BeautifulSoup(parse_response(shop_response), 'html.parser')
product_links = [a['href'] for a in shop_soup.find_all(
    'a', href=re.compile('^/shop/[0-9]+$'))]

# Fetch and parse each product page
for link in product_links:
    response = send_request(link)
    parsed_content = parse_response(response)
    print(f"Content for {link}:\n{parsed_content}\n{'-'*50}\n")
