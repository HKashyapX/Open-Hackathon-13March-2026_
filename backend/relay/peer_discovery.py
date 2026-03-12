import time
from common.packet_schema import create_packet

DISCOVERY_INTERVAL = 10


def discovery_loop(broadcast_func, node_id):
    """
    Periodically broadcasts this node's presence
    so other nodes can discover it.
    """

    while True:

        packet = create_packet(
            packet_type="DISCOVERY",
            sender=node_id,
            payload=node_id
        )

        print("Broadcasting discovery packet:", packet)

        broadcast_func(packet)

        time.sleep(DISCOVERY_INTERVAL)