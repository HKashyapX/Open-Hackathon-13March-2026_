import time

# Stores packet_id → timestamp
seen_packets = {}

# Time (seconds) before a packet expires
CACHE_TTL = 60

# Maximum cache size before cleanup
MAX_CACHE_SIZE = 5000


def seen_before(msg_id):
    """
    Returns True if the packet was already processed.
    """
    return msg_id in seen_packets


def add_packet(msg_id):
    """
    Add packet ID to cache.
    """
    seen_packets[msg_id] = time.time()

    if len(seen_packets) > MAX_CACHE_SIZE:
        cleanup_cache()


def cleanup_cache():
    """
    Remove expired packets.
    """
    now = time.time()

    expired = [
        msg_id for msg_id, timestamp in seen_packets.items()
        if now - timestamp > CACHE_TTL
    ]

    for msg_id in expired:
        del seen_packets[msg_id]


def cache_size():
    """
    Debug helper.
    """
    return len(seen_packets)