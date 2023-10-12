import socket
import threading
import json
import os

HOST = "127.0.0.1"
PORT = 12345
SERVER_MEDIA = "SERVER_MEDIA"

if not os.path.exists(SERVER_MEDIA):
    os.makedirs(SERVER_MEDIA)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen()
print(f"Server is listening on {HOST}:{PORT}")


def handle_client(client_socket, client_address):
    print(f"Accepted connection from {client_address}")
    while True:
        message = client_socket.recv(1024).decode("utf-8")
        if not message:
            break
        message_data = json.loads(message)

        if message_data["type"] == "text":
            print(f"Received from {client_address}: {message}")
            for client in clients:
                if client != client_socket:
                    client.send(message.encode("utf-8"))
        elif message_data["type"] == "file":
            file_path = os.path.join(SERVER_MEDIA, message_data["filename"])
            with open(file_path, "wb") as f:
                f.write(message_data["content"].encode())
            response = {
                "type": "text",
                "message": f"User {message_data['username']} uploaded the file {message_data['filename']}",
                "username": "server",
                "room": message_data["room"],
            }
            for client in clients:
                client.send(json.dumps(response).encode("utf-8"))
        elif message_data["type"] == "download":
            file_path = os.path.join(SERVER_MEDIA, message_data["filename"])
            if os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    content = f.read().decode()
                response = {
                    "type": "file",
                    "filename": message_data["filename"],
                    "content": content,
                    "username": "server",
                    "room": message_data["room"],
                }
                client_socket.send(json.dumps(response).encode("utf-8"))
            else:
                response = {
                    "type": "text",
                    "message": f"The file {message_data['filename']} doesn't exist.",
                    "username": "server",
                    "room": message_data["room"],
                }
                client_socket.send(json.dumps(response).encode("utf-8"))

    clients.remove(client_socket)
    client_socket.close()


clients = []
while True:
    client_socket, client_address = server_socket.accept()
    clients.append(client_socket)
    client_thread = threading.Thread(
        target=handle_client, args=(client_socket, client_address)
    )
    client_thread.start()
