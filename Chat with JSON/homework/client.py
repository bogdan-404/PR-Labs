import socket
import threading
import json
import os

HOST = "127.0.0.1"
PORT = 12345

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))
print(f"Connected to {HOST}:{PORT}")
username = input("Enter a username: ")
room = input("Enter a room: ")

MEDIA = username
if not os.path.exists(MEDIA):
    os.makedirs(MEDIA)


def receive_messages():
    while True:
        message = client_socket.recv(1024).decode("utf-8")
        if not message:
            break
        message_data = json.loads(message)

        if message_data["room"] == room:
            if message_data["type"] == "text":
                print(f"\n{message_data['username']}: {message_data['message']}")
            elif message_data["type"] == "file":
                with open(os.path.join(MEDIA, message_data["filename"]), "wb") as f:
                    f.write(message_data["content"].encode())


def send_messages():
    while True:
        message = input("")
        if message.lower() == "exit":
            break
        if message.startswith("upload:"):
            filepath = message.split(":", 1)[1].strip()
            if os.path.exists(filepath):
                with open(filepath, "rb") as f:
                    content = f.read().decode()
                payload = {
                    "type": "file",
                    "filename": os.path.basename(filepath),
                    "content": content,
                    "username": username,
                    "room": room,
                }
                client_socket.send(json.dumps(payload).encode("utf-8"))
            else:
                print(f"File {filepath} doesn't exist.")
        elif message.startswith("download:"):
            filename = message.split(":", 1)[1].strip()
            payload = {
                "type": "download",
                "filename": filename,
                "filetype": "file",
                "username": username,
                "room": room,
            }
            client_socket.send(json.dumps(payload).encode("utf-8"))
        else:
            payload = {
                "type": "text",
                "message": message,
                "username": username,
                "room": room,
            }
            client_socket.send(json.dumps(payload).encode("utf-8"))


receive_thread = threading.Thread(target=receive_messages)
receive_thread.daemon = True
receive_thread.start()

send_thread = threading.Thread(target=send_messages)
send_thread.daemon = True
send_thread.start()

receive_thread.join()
send_thread.join()
