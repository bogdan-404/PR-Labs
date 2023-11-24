import os
import logging


class RaftNode:
    def __init__(self, node_id, lock_file_path):
        self.node_id = node_id
        self.state = "follower"
        self.lock_file_path = lock_file_path
        self.elect_leader()

    def elect_leader(self):
        try:
            with open(self.lock_file_path, "x") as lock_file:
                lock_file.write(self.node_id)
            self.state = "leader"
        except FileExistsError:
            with open(self.lock_file_path, "r") as lock_file:
                leader_id = lock_file.read()
            self.state = "leader" if leader_id == self.node_id else "follower"
        logging.info(f"Node {self.node_id} initialized as {self.state}")
