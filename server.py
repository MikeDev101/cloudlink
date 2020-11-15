"""
MikeDEV's CloudLink Server
CloudLink is a websocket extension for Scratch 3.0, which allows MMOs, Web Browsers, BBSs, chats, and more, all using Scratch 3.0. It's cloud variables, but better. 
Origial concept created in 2018.
Rewritten in 2020.
For more details about CloudLink, please visit
https://github.com/MikeDev101/cloudlink
"""

vers = "B2.3"

import asyncio, json, websockets, sys, threading, ssl

PORT = 3000 #Define default port if the code runs on it's own
enable_verbose_events = False #Leave verbose events off by default

global USERNAMES

STREAMS = {"gs": "", "dd":""} #Define data streams, will improve upon this design later
USERS = set() #create unorganized, non-indexed set of users
USERNAMES = [] #create organized, indexable list of users

"""#WS over SSL for WSS support
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain("cert.pem", "key.pem")"""

class CloudLink(object):
    def __init__(self, loop):
        self.loop = loop

    async def notify_state_global():
        if USERS:
            message = json.dumps({"type":"gs","data":str(STREAMS["gs"])}) # Send global data to every client
            await asyncio.wait([user.send(message) for user in USERS])

    async def notify_state_private(e):
        if USERS:
            message = json.dumps({"type":"ps","data":str(STREAMS[e]),"id":str(e)}) #Send private data to every client, only one client will store the data, others will ignore
            #await asyncio.wait([user.send(message) for user in USERS])
            for user in USERS:
              await asyncio.wait([user.send(message)])

    async def notify_state_disk(e):
        if USERS:
            message = json.dumps({"type":"dd","data":str(STREAMS[e]),"id":str(e)}) #Send CloudDisk data to every client, only one client will store the data, others will ignore
            #await asyncio.wait([user.send(message) for user in USERS])
            for user in USERS:
              await asyncio.wait([user.send(message)])
    
    async def notify_state_ftp(e):
        if USERS:
            message = json.dumps({"type":"ftp","data":str(STREAMS[e]),"id":str(e)}) #Send CloudDisk FTP data to every client, only one client will store the data, others will ignore
            #await asyncio.wait([user.send(message) for user in USERS])
            for user in USERS:
              await asyncio.wait([user.send(message)])

    async def notify_state_coin(e):
        if USERS:
            message = json.dumps({"type":"cd","data":str(STREAMS[e]),"id":str(e)}) #Send CloudCoin data to every client, only one client will store the data, others will ignore
            #await asyncio.wait([user.send(message) for user in USERS])
            for user in USERS:
              await asyncio.wait([user.send(message)])
    
    async def notify_state_account(e):
        if USERS:
            message = json.dumps({"type":"ca","data":str(STREAMS[e]),"id":str(e)}) #Send CloudAccount data to every client, only one client will store the data, others will ignore
            #await asyncio.wait([user.send(message) for user in USERS])
            for user in USERS:
              await asyncio.wait([user.send(message)])

    async def update_username_lists():
        if USERS:
            y = ""
            for x in range(len(USERNAMES)):
                y = str(y + USERNAMES[x] + ";")
            message = json.dumps({"type":"ul","data":str(y)}) #Send username list to all clients
            #await asyncio.wait([user.send(message) for user in USERS])
            for user in USERS:
              await asyncio.wait([user.send(message)])

    async def refresh_username_lists():
        if USERS:
          for user in USERS:
            await asyncio.wait([user.send(json.dumps({"type":"ru","data":""}))])

    async def register(websocket): #Create client session
        USERS.add(websocket)

    async def unregister(websocket): #End client session
        USERS.remove(websocket)

    async def server(websocket, path):
        global USERNAMES
        await CloudLink.register(websocket)
        await CloudLink.notify_state_global()
        await CloudLink.update_username_lists()
        try:
            await websocket.send(json.dumps({"type":"gs","data":str(STREAMS["gs"])}))
            async for message in websocket:
                data = message.split("\n")
                if enable_verbose_events:
                    print("[ i ] Got packet: "+str(data))
                if data[0] == "<%gs>": # Global stream update command
                    STREAMS["gs"] = str(data[2])
                    await CloudLink.notify_state_global()
                elif data[0] == "<%ps>": # Private stream update command
                    if data[2] in USERNAMES:
                        STREAMS[str(data[2])] = str(data[3])
                        await CloudLink.notify_state_private(str(data[2]))
                elif data[0] == "<%dd>": # CloudDisk API update command
                    if data[2] in USERNAMES:
                        STREAMS[str(data[2])] = str(data[3])
                        await CloudLink.notify_state_disk(str(data[2]))
                elif data[0] == "<%cd>": # CloudCoin API update command
                    if data[2] in USERNAMES:
                        STREAMS[str(data[2])] = str(data[3])
                        await CloudLink.notify_state_coin(str(data[2]))
                elif data[0] == "<%ca>": # CloudAccount API update command
                    if data[2] in USERNAMES:
                        STREAMS[str(data[2])] = str(data[3])
                        await CloudLink.notify_state_account(str(data[2]))
                elif data[0] == "<%ds>": # Disconnect command
                    if data[1] in USERNAMES:
                        print("[ i ] Disconnecting user:", str(data[1]))
                        USERNAMES.remove(str(data[1]))
                        STREAMS.pop(str(data[1]))
                    await CloudLink.unregister(websocket)
                    await CloudLink.update_username_lists()
                elif data[0] == "<%ftp>": # CloudDisk API FTP update command
                    if data[2] in USERNAMES:
                        STREAMS[str(data[2])] = str(data[3])
                        await CloudLink.notify_state_ftp(str(data[2])) 
                elif data[0] == "<%sn>": # Append username command
                    if data[1] == "%CD%":
                        print("[ OK ] Linked to CloudDisk API.")
                    elif data[1] == "%CC%":
                        print("[ OK ] Linked to CloudCoin API.")
                    elif data[1] == "%CA%":
                        print("[ OK ] Linked to CloudAccount API.")
                    else:
                        if not data[1] in USERNAMES:
                            print("[ i ] Connected:", data[1])
                    if not data[1] in USERNAMES:
                        USERNAMES.append(str(data[1]))
                        STREAMS[str(data[1])] = ""
                        await CloudLink.update_username_lists()
                elif data[0] == "<%rf>": # Refresh user list
                    print("[ i ] Refreshing user list...")
                    USERNAMES = []
                    await CloudLink.update_username_lists()
                    await CloudLink.refresh_username_lists()
                else: # Generic unknown command response
                    print("[ ! ] Error: Unknown command:", str(data))
        except Exception as e:
            print("[ ! ] Error: An exception occured. Here's the error:\n"+str(e))
        finally:
            print("[ i ] Disconnect detected...")
            if websocket in USERS:
                await CloudLink.unregister(websocket)
            USERNAMES = []
            await CloudLink.update_username_lists()
            await CloudLink.refresh_username_lists()

if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        cl = CloudLink(loop)
        start_server = websockets.serve(CloudLink.server, "localhost", PORT)
        print("MikeDEV's CloudLink Server - Version " + str(vers) + " | Now running on port " + str(PORT) + ".")
        cl.loop.run_until_complete(start_server)
        cl.loop.run_forever()
    except KeyboardInterrupt:
        print("[ i ] Stopping the CloudLink API server...")
        sys.exit()
    except Exception as e:
        print("[ ! ] Error! Stopping the CloudLink API server... "+str(e))
        sys.exit()