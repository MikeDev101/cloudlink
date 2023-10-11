#!/usr/bin/env python3

version = "0.1.5"

"""
### CloudLink Server ###

Version S3.0 - Developed by MikeDEV Software

CloudLink is a websocket extension developed for Scratch 3.0. It's
designed to make web browsers, MMOs, BBSs, chats, etc. possible within
the limitations of Scratch. For more details and documentation about
the CloudLink project, please see the official repository on Github:
https://github.com/MikeDev101/cloudlink.

0BSD License
Copyright (C) 2020-2021 MikeDEV Software, Co.

Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted.

THE SOFTWARE IS PROVIDED “AS IS” AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
"""

# Import dependencies
import json
import sys
from time import sleep
from threading import *
from websocket_server import WebsocketServer
import websocket

# API class for interacting with the module.
class API:
    def host(self, port, ip=None): # runs the module in server mode, uses websocket-server
        self.mode = 1
        if ip == None:
            self.wss = WebsocketServer(port=port) # Instanciate WebsocketServer alongside CloudLink module
        else:
            self.wss = WebsocketServer(port=port, host=ip) # Instanciate WebsocketServer alongside CloudLink module
            
        # Define callbacks to functions
        self.wss.set_fn_new_client(self._newConnection)
        self.wss.set_fn_message_received(self._gotPacket)
        self.wss.set_fn_client_left(self._closedConnection)
            
        # Create a new thread and make it a daemon thread
        self.serverThread = Thread(target=self.wss.serve_forever)
        self.serverThread.setDaemon(True)
            
        # Run the server
        self.serverThread.start()

    def client(self, ip, on_new_packet=None, on_connect=None, on_error=None): # runs the module in client mode, uses websocket-client
        self.mode = 2
        try:
            self.client = websocket.WebSocketApp(ip, on_message = self._on_message, on_error = self._on_error, on_open = self._on_open)
            
            # Define callbacks to functions
            self._set_fn_new_packet(on_new_packet)
            self._set_fn_connected(on_connect)
            self._set_fn_error(on_error)
            self._set_fn_disconnected(self.stop)
            
            # Create a new thread and make it a daemon thread
            self.clientThread = Thread(target=self.client.run_forever)
            self.clientThread.setDaemon(True)
            
            # Run the client
            self.clientThread.start()
            
        except Exception as e:
            print(e)
            sys.exit()

    def stop(self): # Stops running the module in either host/client mode
        if self.mode == 2:
            self.client.close()
            self.mode = 0
        if self.mode == 1:
            if not len(self.users) == 0:
                print("Shutdown in progress, please wait...")
                # Tell all users to disconnect, and wait until all are disconnected
                while not len(self.users) == 0:
                    self.wss.send_message_to_all(json.dumps({"cmd":"ds"}))
                    sleep(1) # Retry every second
                print("All users disconnected, now exiting...")
            else:
                print("Now exiting...")
            self.wss.server_close()
            self.mode = 0
    
    def sendPacket(self, msg): # Sends packets when the module is running in client mode
        if self.mode == 2:
            self.client.send(json.dumps(msg))

# CloudLink class, containing the API and all of the spaghetti code that makes this weird project work.
class CloudLink(API):
    def __init__(self): # Initializes the class
        self.wss = None
        self.users = {}
        self.userlist = []
        self.handlers = []
        self.gdata = ""
        self.mode = 0 # 1=Host, 2=Client
        print("CloudLink v{0}".format(version))

    def _newConnection(self, client, server): # Server: Handles new connections
        if self.mode == 1:
            print("New connection: {0}".format(client['id']))
            self.users[str(client)] = {"name": "", "id": str(client['id'])}
            self._relayUserList(server, True, client)
            self._sendPacket(server, True, {"cmd":"gmsg", "id":client, "val":str(self.gdata)})
            self._sendPacket(server, True, {"cmd":"direct", "id":client, "val": {"cmd": "vers", "val": version}})

    def _sendPacket(self, server, type, data): # Server: Transmits packets, False:Public, True:Private
        if self.mode == 1:
            if "id" in data:
                id = data["id"]
                del data["id"]
            if type == False:
                server.send_message_to_all(json.dumps(data))
            elif type == True:
                server.send_message(id, json.dumps(data))

    def _relayUserList(self, server, type, id): # Server: Relays the username list to all connected users
        if self.mode == 1:
            y = ""
            for x in range(len(self.userlist)):
                y = str(y + self.userlist[x] + ";")
            self._sendPacket(server, type, {"cmd":"ulist", "id":id, "val":str(y)})

    def _closedConnection(self, client, server): # Server: Handles dropped/lost/manual disconnections
        if self.mode == 1:
            if str(client) in self.users:
                if self.users[str(client)]['name'] in self.userlist:
                    print("Connection closed: {0} ({1})".format(self.users[str(client)]['name'], client['id']))
                else:
                    print("Connection closed: {0}".format(client['id']))
                
                if self.users[str(client)]['name'] in self.userlist:
                    del self.userlist[self.userlist.index(self.users[str(client)]['name'])]
                if client in self.handlers:
                    del self.handlers[self.handlers.index(client)]
                    
                del self.users[str(client)]
                
                if not len(self.users) == 0:
                    self._relayUserList(server, False, client)

    def _gotPacket(self, client, server, message): # Server: Handles new packet events
        if self.mode == 1:
            err = False
            try:
                packet = json.loads(message)
                print("Got packet: {0} bytes".format(len(str(packet))))
            except Exception as e:
                err = True
            finally:
                if not err:
                    if "cmd" in packet: # Check if the cmd parameter is specified
                        cmd = packet['cmd']
                        if "val" in packet:
                            val = packet["val"]
                        else:
                            val = ""
                        if "id" in packet:
                            try:
                                id = self.handlers[self.userlist.index(str(packet['id']))]
                            except Exception as e:
                                id = ""
                        else:
                            id = ""
                        if "name" in packet:
                            name = str(packet['name'])
                        else:
                            name = ""
                        if "origin" in packet:
                            origin = str(packet['origin'])
                        else:
                            origin = ""
                        
                        if cmd == "clear": # Clears comms
                            self._sendPacket(server, False, {"cmd":"gmsg", "val":""})
                            self._sendPacket(server, False, {"cmd":"pmsg", "val":""})
                        if cmd == "setid": # Set username on server link
                            if "val" in packet:
                                if not client in self.handlers:
                                    self.userlist.append(val)
                                    self.handlers.append(client)
                                else:
                                    if self.users[str(client)]['name'] in self.userlist:
                                        self.userlist[self.userlist.index(self.users[str(client)]['name'])] = val
                                self.users[str(client)]['name'] = val
                                print("User {0} declared username: {1}".format(client['id'], self.users[str(client)]['name']))
                                self._relayUserList(server, False, client)
                        if cmd == "gmsg": # Set global stream data values
                            self.gdata = str(val)
                            self._sendPacket(server, False, {"cmd":"gmsg", "val":self.gdata})
                        if cmd == "pmsg": # Set private stream data values
                            if not id == "":
                                if not origin == "":
                                    self._sendPacket(server, True, {"cmd":"pmsg", "id":id, "val":val, "origin":origin})
                        if cmd == "gvar": # Set global variable data values
                            self._sendPacket(server, False, {"cmd":"gvar", "name":name, "val":val})
                        if cmd == "pvar": # Set private variable data values
                            if not id == "":
                                if not origin == "":
                                    self._sendPacket(server, True, {"cmd":"pvar", "name":name, "id":id, "val":val, "origin":origin})

    def _set_fn_new_packet(self, fn): # Client: Defines API-friendly callback to new packet events
        self.fn_msg = fn
    
    def _set_fn_connected(self, fn): # Client: Defines API-friendly callback to connected event
        self.fn_con = fn
    
    def _set_fn_error(self, fn): # Client: Defines API-friendly callback to error event
        self.fn_err = fn
    
    def _set_fn_disconnected(self, fn): # Client: API-friendly Defines callback to disconnected event
        self.fn_ds = fn
    
    def _on_message(self, ws, message): # Client: Defines callback to new packet events
        if not json.loads(message) == {"cmd": "ds"}:
            self.fn_msg(json.loads(message))
        else:
            self.fn_ds()
    
    def _on_error(self, ws, error): # Client: Defines callback to error events
        self.fn_err(error)
        self.fn_ds()
    
    def _on_open(self, ws): # Client: Defines callback to connected event
        self.fn_con()
