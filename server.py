#MikeDEV's CloudLink Server
#Version 1.6b

import asyncio
import json
import websockets

STREAMS = {"ps": ""} #Define data streams, will improve upon this design later
USERS = set() #create unorganized, non-indexed set of users

def state_event():
    return json.dumps(str(STREAMS["ps"]))

def users_event():
    return json.dumps({"type": "users", "count": len(USERS)})


async def notify_state():
    if USERS:  # asyncio.wait doesn't accept an empty list
        message = state_event()
        await asyncio.wait([user.send(message) for user in USERS])


async def register(websocket):
    USERS.add(websocket)
    print("[ i ] A user connected.")


async def unregister(websocket):
    USERS.remove(websocket)
    print("[ i ] A user disconnected.")


async def server(websocket, path):
    await register(websocket)
    try:
        await websocket.send(state_event())
        async for message in websocket:
            data = message.split("\n")
            if data[0] == "<%ps>":
                print("[ i ] Update public stream:", str(data[1]))
                STREAMS["ps"] = str(data[1])
                await notify_state()
            elif data[0] == "<%ds>":
                await unregister(websocket)
            else:
                print("[ ! ] Error: Unknown command:", str(data))
    except:
        await unregister(websocket)

print("MikeDEV's CloudLink Server v1.6b\nNow listening for requests on port 3000.\n")
cl_server = websockets.serve(server, "localhost", 3000)

asyncio.get_event_loop().run_until_complete(cl_server)
asyncio.get_event_loop().run_forever()
