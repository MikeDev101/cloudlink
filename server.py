#MikeDEV's CloudLink Server
#Version 1.8

vers = "1.8"

import asyncio
import json
import websockets

PORT = 3000 #Default port
STREAMS = {"gs": ""} #Define data streams, will improve upon this design later
USERS = set() #create unorganized, non-indexed set of users
USERNAMES = [] #create organized, indexable list of users

def state_event_global(): #Prepare data to be sent to clients on the global data stream
    x = {
        "type":"gs",
        "data":str(STREAMS["gs"])
        }
    return json.dumps(x)

async def notify_state_global():
    if USERS:
        message = state_event_global() # Send global data to every client
        await asyncio.wait([user.send(message) for user in USERS])

def state_event_private(uname): #Prepare data to be sent to specific clients on the private data streams
    y = {
        "type":"ps",
        "data":str(STREAMS[uname]),
        "id":str(uname)
        }
    return json.dumps(y)

async def notify_state_private(e):
    if USERS:
        message = state_event_private(e) #Send private data to every client, only one client will store the data, others will ignore
        await asyncio.wait([user.send(message) for user in USERS])

def prepare_usernames(): # Generate primitive array of usernames
    y = ""
    for x in range(len(USERNAMES)):
        y = str(y + USERNAMES[x] + ";")
    z = {
        "type":"ul",
        "data":str(y)
        }
    return json.dumps(z)

async def update_username_lists():
    if USERS:
        message = prepare_usernames() #Send username list to all clients
        await asyncio.wait([user.send(message) for user in USERS])

async def register(websocket): #Create client session
    USERS.add(websocket)


async def unregister(websocket): #End client session
    USERS.remove(websocket)


async def server(websocket, path):
    await register(websocket)
    await notify_state_global()
    await update_username_lists()
    try:
        await websocket.send(state_event_global())
        async for message in websocket:
            data = message.split("\n")
            if data[0] == "<%gs>": # Global stream update command
                STREAMS["gs"] = str(data[2])
                await notify_state_global()
            elif data[0] == "<%ps>": # Private stream update command
                if data[2] in USERNAMES:
                    STREAMS[str(data[2])] = str(data[3])
                    await notify_state_private(str(data[2]))
            elif data[0] == "<%ds>": # Disconnect command
                if data[1] in USERNAMES:
                    print("[ i ] Disconnecting user:", str(data[1]))
                    USERNAMES.remove(str(data[1]))
                    STREAMS.pop(str(data[1]))
                await unregister(websocket)
                await update_username_lists()
            elif data[0] == "<%sn>": # Append username command
                print("[ i ] User connected:", data[1])
                USERNAMES.append(str(data[1]))
                STREAMS[str(data[1])] = ""
                await update_username_lists()
            else: # Generic unknown command response
                print("[ ! ] Error: Unknown command:", str(data))
    except:
        await unregister(websocket) # If all things fork up, kill the connection

print("MikeDEV's CloudLink Server v" + vers + "\nNow listening for requests on port " + PORT + ".\n")
cl_server = websockets.serve(server, "localhost", PORT)

while True:
    asyncio.get_event_loop().run_until_complete(cl_server)
    asyncio.get_event_loop().run_forever()
