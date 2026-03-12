import uuid


def create_packet(packet_type, sender, payload="", hop_count=0):
    """
    Creates a standardized packet for the mesh network.
    """

    return {
        "msg_id": str(uuid.uuid4()),
        "type": packet_type,
        "sender": sender,
        "payload": payload,
        "hop_count": hop_count
    }