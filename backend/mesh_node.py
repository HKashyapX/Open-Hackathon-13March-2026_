import json
import socket
import threading

from relay.packet_handler import handle_packet
from relay.peer_discovery import discovery_loop
from relay.heartbeat import heartbeat_loop

PORT = 5000


class MeshNode:

    def __init__(self, node_id, port):
        self.node_id = node_id
        self.port = port

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("127.0.0.1", self.port))

    def broadcast(self, packet):

        data = json.dumps(packet).encode()

        self.sock.sendto(data, ("127.0.0.1", PORT))

    def listen(self):

        while True:

            data, addr = self.sock.recvfrom(4096)

            packet = data.decode()

            handle_packet(packet, self.broadcast)

    def start(self):

        threading.Thread(target=self.listen, daemon=True).start()

        threading.Thread(
            target=discovery_loop,
            args=(self.broadcast, self.node_id),
            daemon=True
        ).start()

        threading.Thread(
            target=heartbeat_loop,
            args=(self.broadcast, self.node_id),
            daemon=True
        ).start()

        print(f"Node {self.node_id} running")

        while True:
            pass