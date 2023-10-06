import socket
import threading
import json


HOST = '127.0.0.1'  # Loopback address for localhost
PORT = 12345  # Port to listen on
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen()
print(f"Server is listening on {HOST}:{PORT}")


def handle_client(client_socket, client_address):
    print(f"Accepted connection from {client_address}")
    while True:
        message = client_socket.recv(1024).decode('utf-8')
        message_data = json.loads(message)
        if not message:
            break
        print(f"Received from {client_address}: {message}")
        print(clients)
        for client in clients:
            if client != client_socket:
                message_to_send = json.dumps(message_data)
                client.send(message_to_send.encode('utf-8'))
    clients.remove(client_socket)
    client_socket.close()


clients = []
while True:
    client_socket, client_address = server_socket.accept()
    clients.append(client_socket)
    client_thread = threading.Thread(
        target=handle_client, args=(client_socket, client_address))
    client_thread.start()
