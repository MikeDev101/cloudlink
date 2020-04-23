#MikeDEV's CloudLink Server
#Version 1.0

receivedMessages = ""

#Server imports
import asyncio
import random
import websockets

#Data imports
import json

#Address of the other machine it is connected to
global pairMachine

async def client(websocket, path):
    global receivedMessages
    while True:
        data = await websocket.recv()
        if data == "%_fetch":
            #If no messages
            if receivedMessages == []:
                await websocket.send("")
                
            else:
                await websocket.send(json.dumps(receivedMessages))
        else:
            receivedMessages = str(data)

print("MikeDEV's CloudLink Server v1.0\nNow hosting from ws://127.0.0.1:3000/.")
start_server = websockets.serve(client, '127.0.0.1', 3000)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
