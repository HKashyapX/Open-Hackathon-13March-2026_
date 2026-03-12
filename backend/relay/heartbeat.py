import time
from common.packet_schema import create_packet

HEARTBEAT_INTERVAL = 5


def heartbeat_loop(broadcast_func, node_id):
    """
    Periodically sends heartbeat packets so other nodes
    know this node is still active.
    """

    while True:

        packet = create_packet(
            packet_type="HEARTBEAT",
            sender=node_id,
            payload=""
        )

        print("Sending heartbeat:", packet)

        broadcast_func(packet)

        time.sleep(HEARTBEAT_INTERVAL)