from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
import aegis_node
import threading
import time
import uvicorn
from contextlib import asynccontextmanager

MY_IP = "10.213.230.220"       # ← Node Beta: "10.213.230.200"
NODE_NAME = "Node-Alpha"       # ← Node Beta: "Node-Beta"

node = aegis_node.AegisNode(port=5005, node_name=NODE_NAME, local_ip=MY_IP)

def run_background():
    threading.Thread(target=node.listen, daemon=True).start()
    while True:
        node.broadcast_presence()
        time.sleep(5)

@asynccontextmanager
async def lifespan(app: FastAPI):
    threading.Thread(target=run_background, daemon=True).start()
    yield

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/peers")
def get_peers():
    return {"peers": list(node.peers.keys())}

@app.get("/messages")
def get_messages():
    return {"messages": node.message_log}

@app.post("/send")
def send_fragmented_msg(data: dict = Body(...)):
    receiver_id = data.get("receiver_id", "ALL")
    message = data.get("message")
    
    if not message:
        return {"error": "Missing data"}

    if receiver_id == "ALL":
        targets = list(node.peers.keys())
    else:
        targets = [receiver_id] if receiver_id in node.peers else []

    if not targets:
        return {"error": "No valid targets"}

    for target in targets:
        node.send_hop_message(message, target)
        
    return {"status": "sent"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)