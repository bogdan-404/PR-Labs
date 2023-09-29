import socket
import signal
import sys
import threading
import json


HOST = '127.0.0.1'
PORT = 8080
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)
print(f"Server is listening on {HOST}:{PORT}")


def handle_request(client_socket):
    request_data = client_socket.recv(1024).decode('utf-8')
    print(f"Received Request:\n{request_data}")
    request_lines = request_data.split('\n')
    request_line = request_lines[0].strip().split()
    path = request_line[1]
    response_content = ''
    status_code = 200
    if path == '/home':
        response_content = '<h1>Main Page</h1><a href="/about">About Page</a><div><a href="/shop">Buy Our Books</a></div>'
    elif path == '/about':
        response_content = '<h1>We are selling books</h1><p>Shop our programming books:<p><a href="/shop">Buy Books</a><p>Go to Home Page:</p><a href="/home">Home Page</a>'
    elif path == '/shop':
        with open('data.json', 'r') as f:
            books = json.load(f)
        response_content = '<h1>Available books</h1><div><ul>'
        for book in books:
            response_content += f'<li><a href="/shop/{book["id"]}">{book["name"]}</a></li>'
        response_content += '</ul></div><p>Go to Home Page:</p><a href="/home">Home Page</a>'
    elif path.startswith('/shop/'):
        with open('data.json', 'r') as f:
            books = json.load(f)
        book_id = path[-1]
        print(book_id)
        book = None
        for b in books:
            if int(b['id']) == int(book_id):
                book = b
                break
        if book:
            response_content = f'<h1>Book Details</h1><ul><li>Title: {book["name"]}</li><li>Author: {book["author"]}</li><li>Price: {book["price"]}</li><li>Small Description: {book["description"]}</li></ul></p><div><a href="/shop">Go Back</a></div>'
        else:
            response_content = '404 Not Found'
            status_code = 404
    else:
        response_content = '404 Not Found'
        status_code = 404
    response = f'HTTP/1.1 {status_code} OK\nContent-Type: text/html\n\n{response_content}'
    client_socket.send(response.encode('utf-8'))
    client_socket.close()


def signal_handler(sig, frame):
    print("\nShutting down the server...")
    server_socket.close()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
while True:
    client_socket, client_address = server_socket.accept()
    client_handler = threading.Thread(
        target=handle_request, args=(client_socket,))
    client_handler.start()
