import socket
import json
import threading
from nacl.public import PrivateKey, Box
import nacl.utils

class AegisNode:
    def __init__(self, port=5005):
        self.port = port
        self.priv_key = PrivateKey.generate()
        self.pub_key = self.priv_key.public_key
        self.peers = {} 
        self.message_history = set() 
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.bind(('', self.port))

    def listen(self):
        print(f"AegisNode listening on {self.port}...")
        while True:
            data, addr = self.sock.recvfrom(4096)
            try:
                packet = json.loads(data.decode())
                msg_id = packet.get("msg_id")
                if msg_id in self.message_history:
                    continue
                
                self.message_history.add(msg_id)
                if packet['type'] == 'DISCOVERY':
                    peer_id = packet['sender_id']
                    self.peers[peer_id] = packet['pub_key']
                    print(f"Discovered peer: {peer_id} at {addr}")
            except Exception as e:
                continue

    def broadcast_presence(self, node_name="Leo-Fedora"):
        packet = {
            "type": "DISCOVERY",
            "sender_id": node_name,
            "pub_key": self.pub_key.encode().hex(),
            "msg_id": nacl.utils.random(8).hex()
        }
        raw_packet = json.dumps(packet).encode()
        self.sock.sendto(raw_packet, ('<broadcast>', self.port))

# THIS PART MUST BE AT THE VERY LEFT MARGIN (OUTSIDE THE CLASS)
if __name__ == "__main__":
    node = AegisNode()
    
    listener_thread = threading.Thread(target=node.listen, daemon=True)
    listener_thread.start()
    
    print("Broadcasting identity... Press Ctrl+C to stop.")
    try:
        while True:
            node.broadcast_presence()
            import time
            time.sleep(5)
    except KeyboardInterrupt:
        print("\nNode shutting down.")