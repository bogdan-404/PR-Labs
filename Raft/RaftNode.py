import socket
import threading
import time
import random
import requests


class RaftNode:
    def __init__(self, node_id, peers):
        self.node_id = node_id
        self.state = "follower"
        self.peers = peers
        self.start_election_thread()
        self.follower_credentials = {}

    def start_election_thread(self):
        election_thread = threading.Thread(target=self.run_election_cycle)
        election_thread.daemon = True
        election_thread.start()

    def run_election_cycle(self):
        while True:
            time.sleep(random.uniform(5, 10))
            if self.state != "leader":
                self.start_election()

    def start_election(self):
        self.state = "candidate"
        election_port = 10000
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            udp_socket.bind(("", election_port))
            self.state = "leader"
        except socket.error:
            self.state = "follower"
        finally:
            udp_socket.close()

    def update_follower_list(self, follower_address):
        if follower_address not in self.follower_credentials:
            self.follower_credentials[follower_address] = {
                "ip": follower_address.split(":")[0],
                "port": follower_address.split(":")[1],
            }

    def forward_request_to_followers(self, endpoint, data):
        if self.state == "leader":
            for follower in self.follower_credentials.values():
                try:
                    follower_address = f"{follower['ip']}:{follower['port']}"
                    requests.post(f"http://{follower_address}{endpoint}", json=data)
                except requests.RequestException:
                    pass
