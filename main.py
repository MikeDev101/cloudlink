from cloudlink import cloudlink
from cloudlink.protocols import clpv4
from fastapi import FastAPI, WebSocket
import random
import uvicorn

global idnum
idnum = 0

# Create application
cl = cloudlink.server()
app = FastAPI(title='WebSocket Example')

# Monkey-patch code to support FastAPI
async def connection_loop(client):
    while True:
        message = await client.receive_text()
        print(message)
        await cl.message_processor(client, message)

async def execute_unicast(client, message):
    # Guard clause
    if type(message) not in [dict, str]:
        raise TypeError("Supported datatypes for messages are dicts and strings, got type {type(message)}.")
    
    # Convert dict to JSON
    if type(message) == dict:
        message = cl.ujson.dumps(message)
    
    await client.send_text(message)

# Finish monkey-patch
cl.connection_loop = connection_loop
cl.execute_unicast = execute_unicast

# Declare websocket endpoint
@app.websocket("/")
async def websocket_endpoint(client: WebSocket):
    global idnum
    await client.accept()
    
    # Fix unresolved attributes
    client.id = idnum
    idnum += 1
    client.remote_address = (client.client.host, client.client.port)
    
    # Execute the command handler
    await cl.connection_handler(client)

if __name__ == "__main__":

    # Set logging level
    cl.logging.basicConfig(
        format="[%(asctime)s] %(levelname)s: %(message)s",
        level=cl.logging.INFO
    )
    
    # Load CL4 protocol
    clpv4(cl)
    
    # Start the server
    uvicorn.run(app, port=3000, log_level="debug")
