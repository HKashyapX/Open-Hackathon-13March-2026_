from relay.packet_handler import handle_packet

# Fake broadcast function to simulate sending packets
def broadcast(packet):
    print("\nREBROADCASTING PACKET:")
    print(packet)


# Simulated incoming packet
packet = {
    "msg_id": "test123",
    "type": "DATA",
    "sender": "nodeA",
    "payload": "Hello mesh network",
    "hop_count": 0
}

print("Sending packet into handler...\n")

handle_packet(packet, broadcast)