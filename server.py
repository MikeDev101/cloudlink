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
    while True:
        try:
            data = await websocket.recv()
            print(str(data))
            dStream = str(data)
            await websocket.send(json.dumps(dStream))
        except:
            pass

print("MikeDEV's CloudLink Server v1.6\nNow listening for requests on port 3000.\n")
server = websockets.serve(client, '127.0.0.1', 3000)

while True:
    asyncio.get_event_loop().run_until_complete(server)
    asyncio.get_event_loop().run_forever()
