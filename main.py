from cloudlink import cloudlink
from cloudlink.protocols import clpv4
#from fastapi import FastAPI, WebSocket
from sanic import Sanic, Request, Websocket, json
import sys
from functools import partial
from sanic.worker.loader import AppLoader
import random
import uvicorn

global idnum
idnum = 0

cl = cloudlink.server()

cl.logging.basicConfig(
    format="[%(asctime)s] %(levelname)s: %(message)s",
    level=cl.logging.DEBUG
)

clpv4(cl)

def fastapi_monkeypatch():
    app = FastAPI(title='WebSocket Example')

    # Monkey-patch code to support FastAPI
    async def connection_loop(client):
        while True:
            try:
                message = await client.receive_text()
                await cl.message_processor(client, message)
            except Exception as e:
                print(e)
                break

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
    
    
    
    # Load CL4 protocol
    clpv4(cl)
    
    # Start the server
    uvicorn.run(app, port=3000)

def vanilla():
    cl.run(port=3000)

def attach_endpoints(app: Sanic):
    @app.websocket("/")
    async def feed(request: Request, ws: Websocket):
        global idnum
        
        # Fix unresolved attributes
        ws.id = idnum
        idnum += 1
        ws.remote_address = ("127.0.0.1", 3000)
        
        # Execute the command handler
        await cl.connection_handler(ws)

def create_app(app_name: str) -> Sanic:
    app = Sanic(app_name)
    attach_endpoints(app)
    return app

async def connection_loop(client):
    try:
        async for message in client:
            await cl.message_processor(client, message)
    except Exception as e:
        print(e)

cl.connection_loop = connection_loop

if __name__ == "__main__":
    #vanilla()
    #monkeypatch()
    
    # Start sanic server
    app_name = "test"
    loader = AppLoader(factory=partial(create_app, app_name))
    app = loader.load()
    app.prepare(port=3000, dev=True)
    Sanic.serve(primary=app, app_loader=loader)