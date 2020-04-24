# -*- coding: utf-8 -*-
#MikeDEV's CloudLink Server
#Version 1.5

#Define our stream links, first is the public stream link.
publicStream = ""
#Next, we define our private links. Because we want to have more than one link, these will be arrays.
privateStreamsNames = []
#Names act as a way to index the data.
privateStreamsData = []
#Data is where, well, the data is.

#Import the libraries we need.
import asyncio
import random
import websockets
import json

#Address of the other machine it is connected to, but tbh I really don't know what this does.
global pairMachine

#Primary script that does all of our magic...
async def client(websocket, path):
    global publicStream, privateStreams
    while True:
        try:
            data = await websocket.recv()
            splitdata = data.split('\n')
            if splitdata[0] == "%_fetch":
                if splitdata[1] == "@a":
                    await websocket.send(json.dumps(publicStream))
                elif splitdata[1] == "@u":
                    await websocket.send(json.dumps(privateStreamsNames))
                else:
                    if splitdata[1] in privateStreamsNames:
                        await websocket.send(json.dumps(privateStreamsData[privateStreamsNames.index(splitdata[1])]))
                    else:
                        await websocket.send(json.dumps("Error"))
            elif splitdata[0] == '%_con':
                if not splitdata[1] in privateStreamsNames:
                    privateStreamsNames.append(splitdata[1])
                    privateStreamsData.append("")
                    print('"' + str(splitdata[1]) + '" has connected.')
                    print('There is now ' + str(len(privateStreamsNames)) + ' connections.\n')
            elif splitdata[0] == '%_dis':
                if splitdata[1] in privateStreamsNames:
                    del privateStreamsData[privateStreamsNames.index(splitdata[1])]
                    privateStreamsNames.pop(privateStreamsNames.index(splitdata[1]))
                    print('"' + str(splitdata[1]) + '" disconnected.')
                    if len(privateStreamsNames) == 0:
                        print('There are now no connections.\n')
                    else:
                        print('There is now ' + str(len(privateStreamsNames)) + ' connections.\n')
            elif splitdata[0] == '@a':
                publicStream = str(splitdata[1])
            else:
                if splitdata[0] in privateStreamsNames:
                    privateStreamsData[privateStreamsNames.index(splitdata[0])] = str(splitdata[1])
        except:
            pass

print("MikeDEV's CloudLink Server v1.5\nNow listening for requests on port 3000.\n")
server = websockets.serve(client, '127.0.0.1', 3000)

while True: #not needed, but will help prevent errors when trying to run this script through stuff like heroku...
    asyncio.get_event_loop().run_until_complete(server)
    asyncio.get_event_loop().run_forever()
