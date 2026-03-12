from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
import aegis_node
import threading

app = FastAPI()
node = aegis_node.AegisNode()

# Allow your friend's React UI to talk to this Python server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    # Start the listening thread for peer discovery
    threading.Thread(target=node.listen, daemon=True).start()

@app.get("/peers")
def get_peers():
    # Return the list of IDs discovered on the network
    return {"peers": list(node.peers.keys())}

@app.post("/send")
def send_fragmented_msg(receiver_id: str = Body(...), message: str = Body(...)):
    # Trigger the 3-part fragmentation logic
    node.fragment_and_send(receiver_id, message)
    return {"status": "Message split and broadcasted to mesh"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)