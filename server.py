# -*- coding: utf-8 -*-
#MikeDEV's CloudLink Server
#Version 1.6

dStream = ""

import asyncio
import websockets
import json

#Primary script that does all of our magic...
async def client(websocket, path):
    global dStream
    await websocket.send(json.dumps(dStream)) # Update the new client with the latest data
    while True: # Loop forever, relay data between clients
        try:
            data = await websocket.recv()
            print(str(data))
            dStream = str(data)
            await websocket.send(json.dumps(dStream))
        except:
            pass

# Print version and info :)
print("MikeDEV's CloudLink Server v1.6\nNow listening for requests on port 3000.\n")
server = websockets.serve(client, '127.0.0.1', 3000)

# Main thread loop, run the server script infinitely 
asyncio.get_event_loop().run_until_complete(server)
asyncio.get_event_loop().run_forever()
