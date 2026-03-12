import json
import random
import time

from relay.packet_cache import seen_before, add_packet
from common.packet_schema import create_packet


MAX_HOPS = 5
FORWARD_PROBABILITY = 0.7


def handle_packet(packet, broadcast_func):
    """
    Processes incoming packets and relays them.
    """

    # Convert JSON string to dictionary
    if isinstance(packet, str):
        packet = json.loads(packet)

    msg_id = packet["msg_id"]

    # Drop duplicate packets
    if seen_before(msg_id):
        return

    add_packet(msg_id)

    # Drop packets exceeding hop limit
    if packet["hop_count"] >= MAX_HOPS:
        return

    packet_type = packet["type"]

    if packet_type == "DATA":
        print("DATA received:", packet["payload"])

    elif packet_type == "DISCOVERY":
        print("New peer discovered:", packet["sender"])

    elif packet_type == "HEARTBEAT":
        print("Heartbeat from:", packet["sender"])

    else:
        print("Unknown packet type:", packet_type)

    # Increase hop count before forwarding
    packet["hop_count"] += 1

    # Random delay to reduce broadcast storms
    time.sleep(random.uniform(0.02, 0.2))

    # Probabilistic gossip forwarding
    if random.random() > FORWARD_PROBABILITY:
        return

    # Rebroadcast packet
    broadcast_func(packet)