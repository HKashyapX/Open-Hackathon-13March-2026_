import socket
import json
import threading
import time
from nacl.public import PrivateKey
import nacl.utils

class AegisNode:
    def __init__(self, port=5005, node_name="Node-Alpha", local_ip="0.0.0.0"):
        self.port = port
        self.node_name = node_name
        self.local_ip = local_ip
        self.priv_key = PrivateKey.generate()
        self.pub_key = self.priv_key.public_key
        self.peers = {}
        self.message_history = set()
        self.shard_buffer = {}
        self.shard_meta = {}
        self.message_log = []

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.settimeout(1.0)
        self.sock.bind(('0.0.0.0', self.port))

        self.send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.send_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.send_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.send_sock.bind((self.local_ip, 0))

    def listen(self):
        print(f"[{self.node_name}] Listening on 0.0.0.0:{self.port}...")
        while True:
            try:
                data, addr = self.sock.recvfrom(4096)
                packet = json.loads(data.decode())
                msg_id = packet.get("msg_id")

                if msg_id in self.message_history:
                    continue
                self.message_history.add(msg_id)

                if packet.get('type') == 'DISCOVERY':
                    peer_id = packet.get('sender_id')
                    if peer_id and peer_id != self.node_name:
                        self.peers[peer_id] = {
                            "pub_key": packet.get('pub_key'),
                            "ip": addr[0]
                        }
                        print(f"[{self.node_name}] DISCOVERED: {peer_id} at {addr[0]}")

                elif packet.get('type') == 'SHARD':
                    self._handle_shard(packet)

            except socket.timeout:
                continue
            except Exception as e:
                print(f"[{self.node_name}] listen() error: {e}")
                continue

    def _handle_shard(self, packet):
        message_id   = packet.get("message_id")
        shard_index  = packet.get("shard_index")
        total_shards = packet.get("total_shards")
        data         = packet.get("data")
        sender_id    = packet.get("sender_id")

        if not all([message_id, shard_index, total_shards, data is not None]):
            return

        if message_id not in self.shard_buffer:
            self.shard_buffer[message_id] = {}
            self.shard_meta[message_id]   = total_shards

        self.shard_buffer[message_id][shard_index] = data

        received = len(self.shard_buffer[message_id])
        print(f"[{self.node_name}] Shard {shard_index}/{total_shards} received "
              f"(have {received}/{total_shards}) for msg {message_id[:8]}")

        if received == total_shards:
            ordered = [self.shard_buffer[message_id][i]
                       for i in sorted(self.shard_buffer[message_id])]
            full_message = "".join(ordered)
            print(f"[{self.node_name}] ✅ REASSEMBLED: '{full_message}'")

            # Dedup: only log if not already in last 5 messages
            if not any(m["text"] == full_message and m["peer"] == sender_id
                       for m in self.message_log[-5:]):
                self.message_log.append({
                    "direction": "received",
                    "peer": sender_id,
                    "text": full_message,
                    "time": time.strftime("%H:%M:%S")
                })

            del self.shard_buffer[message_id]
            del self.shard_meta[message_id]

    def broadcast_presence(self):
        packet = {
            "type": "DISCOVERY",
            "sender_id": self.node_name,
            "pub_key": self.pub_key.encode().hex(),
            "msg_id": nacl.utils.random(8).hex()
        }
        raw_packet = json.dumps(packet).encode()

        try:
            self.send_sock.sendto(raw_packet, ('10.213.230.255', self.port))
            print(f"[{self.node_name}] Broadcast sent to 10.213.230.255")
        except Exception as e:
            print(f"[{self.node_name}] Subnet broadcast failed: {e}")

        for i in range(1, 255):
            target = f"10.213.230.{i}"
            if target == self.local_ip:
                continue
            try:
                self.send_sock.sendto(raw_packet, (target, self.port))
            except Exception:
                continue

    def send_hop_message(self, message, target_node_id):
        if target_node_id not in self.peers:
            print(f"[{self.node_name}] Unknown peer: {target_node_id}")
            return

        target_ip    = self.peers[target_node_id]["ip"]
        message_id   = nacl.utils.random(8).hex()
        shard_size   = max(1, len(message) // 3 + 1)
        shards       = [message[i:i + shard_size] for i in range(0, len(message), shard_size)]
        total_shards = len(shards)

        print(f"[{self.node_name}] Sending '{message}' as {total_shards} shards to {target_node_id}")
        self.message_log.append({
            "direction": "sent",
            "peer": target_node_id,
            "text": message,
            "time": time.strftime("%H:%M:%S")
        })

        for _ in range(3):
            for idx, shard_data in enumerate(shards):
                packet = {
                    "type":         "SHARD",
                    "sender_id":    self.node_name,
                    "message_id":   message_id,
                    "shard_index":  idx + 1,
                    "total_shards": total_shards,
                    "data":         shard_data,
                    "msg_id":       nacl.utils.random(8).hex()
                }
                try:
                    self.send_sock.sendto(json.dumps(packet).encode(), (target_ip, self.port))
                except Exception as e:
                    print(f"[{self.node_name}] Shard send failed: {e}")
                time.sleep(0.01)