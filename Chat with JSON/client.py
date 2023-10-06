import socket
import threading
import json


HOST = '127.0.0.1'  # Server's IP address
PORT = 12345  # Server's port
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))
print(f"Connected to {HOST}:{PORT}")
username = input("Enter a username: ")
room = input("Enter a room: ")


def receive_messages():
    while True:
        message = client_socket.recv(1024).decode('utf-8')
        if not message:
            break  
        message_data = json.loads(message)
        if message_data['room'] == room:
            print(f"\n{message_data['username']}: {message_data['payload']}")


def send_messages():
    while True:
        message = input("")
        if message.lower() == 'exit':
            break
        payload = json.dumps(
            {"username": username, "payload": message, "room": room})
        client_socket.send(payload.encode('utf-8'))
    client_socket.close()


receive_thread = threading.Thread(target=receive_messages)
receive_thread.daemon = True  
receive_thread.start()

send_thread = threading.Thread(target=send_messages)
send_thread.daemon = True  
send_thread.start()

receive_thread.join()
send_thread.join()
