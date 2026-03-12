from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
import aegis_node
import threading

app = FastAPI()
node = aegis_node.AegisNode()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    threading.Thread(target=node.listen, daemon=True).start()

@app.get("/peers")
def get_peers():
    return {"peers": list(node.peers.keys())}

@app.post("/send")
def send_fragmented_msg(data: dict = Body(...)):
    # Extracting from the JSON body sent by your frontend
    receiver_id = data.get("receiver_id")
    message = data.get("message")
    
    if not receiver_id or not message:
        return {"error": "Missing receiver_id or message"}

    # SYNCED: This now matches the function name in aegis_node.py
    node.send_hop_message(message, receiver_id)
    return {"status": f"Message '{message}' sharded and sent to {receiver_id}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)