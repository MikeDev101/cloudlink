#!/usr/bin/env python3

"""
### CloudLink Server ###

Version S3.0 - Developed by MikeDEV Software

CloudLink is a websocket extension developed for Scratch 3.0. It's
designed to make web browsers, MMOs, BBSs, chats, etc. possible within
the limitations of Scratch. For more details and documentation about
the CloudLink project, please see the official repository on Github:
https://github.com/MikeDev101/cloudlink. CloudLink is licenced under
the Unlicence Licence.

This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any
means.

In jurisdictions that recognize copyright laws, the author or authors
of this software dedicate any and all copyright interest in the
software to the public domain. We make this dedication for the benefit
of the public at large and to the detriment of our heirs and
successors. We intend this dedication to be an overt act of
relinquishment in perpetuity of all present and future rights to this
software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

For more information, please refer to http://unlicense.org/.
"""

# These libraries should be present on all machines universally. If not, well, I'm not sure how to fix it.
import json
import sys
from os import system, name
from time import sleep

# These booleans determine what modes the CloudLink module can use.
clientOrPluginModeSupport = False
serverModeSupport = False

# This checks for the required dependencies and enables features if those dependencies are met.
try:
    from websocket_server import WebsocketServer
    serverModeSupport = True
except:
    pass

try:
    import websocket
    clientOrPluginModeSupport = True
except:
    pass

# Print the output of what the above code found...
if (not serverModeSupport) and (not clientOrPluginModeSupport):
    print("Hmm. Looks like you have a problem on your hands.\nYou don't have either the websocket_server.py present or websocket-client library installed.\nCloudLink is pretty useless without them.\n")
else:
    print("\nCloudLink S3.0 - Presented by MikeDEV Software - Unlicense License\n")
    if (not serverModeSupport) or (not clientOrPluginModeSupport):
        if serverModeSupport:
            print("You can only use CloudLink in Server mode,\nsince you don't have the websocket-client library installed.\nConsider using 'pip install websocket-client' to use client or plugin modes.\n")
        elif clientOrPluginModeSupport:
            print("You can only use CloudLink in Client/Plugin mode(s),\nsince you don't have the websocket_server.py present in the same directory as cloudlink.py.\nConsider fetching a copy of websocket_server from Github to use server mode.\n")

# This is the main CloudLink class, which contains the entirety of CloudLink.
class CloudLink:
    def __init__(self):
        self.wss = None
        self.users = {}
        self.userlist = []
        self.handlers = []
        self.gdata = ""
        self.mode = 0 # 1=Host, 2=Client, 3=Plugin

    def host(self, port):
        if serverModeSupport:
            self.mode = 1
            self.wss = WebsocketServer(int(port)) # Instanciate WebsocketServer alongside CloudLink module
            
            # Define callbacks to functions
            self.wss.set_fn_new_client(self.newConnection)
            self.wss.set_fn_message_received(self.gotPacket)
            self.wss.set_fn_client_left(self.closedConnection)
            
            # Run the server
            print("Now running in host mode on port {0}...".format(port))
            try:
                self.wss.serve_forever()
            except KeyboardInterrupt:
                if not len(self.users) == 0:
                    print("Shutdown in progress, please wait...")
                    # Tell all users to disconnect, and wait until all are disconnected
                    self.wss.send_message_to_all(json.dumps({"cmd":"ds"}))
                    while not len(self.users) == 0:
                        pass
                    print("All users disconnected, now exiting...")
                else:
                    print("Now exiting...")
                self.wss.server_close()
        else:
            print("Error! Couldn't initialize mode 1: Support for Server mode has been disabled since you don't have the required websocket_server.py!")
            sys.exit()

    def client(self):
        if clientOrPluginModeSupport:
            self.mode = 2
            print("Oops. This is a WIP feature. Sorry...")
            sys.exit()
        else:
            print("Error! Couldn't initialize mode 2: Support for Client mode has been disabled since you don't have the required library websocket-client!")
            sys.exit()

    def plugin(self):
        if clientOrPluginModeSupport:
            self.mode = 3
            print("Oops. This is a WIP feature. Sorry...")
            sys.exit()
        else:
            print("Error! Couldn't initialize mode 3: Support for Plugin mode has been disabled since you don't have the required library websocket-client!")
            sys.exit()

    def newConnection(self, client, server):
        if self.mode == 1:
            print("New connection: {0}".format(client['id']))
            self.users[str(client)] = {"name": "", "id": str(client['id'])}
            self.relayUserList(server, True, client)
            self.sendPacket(server, True, {"cmd":"gmsg", "id":client, "val":str(self.gdata)})

    def sendPacket(self, server, type, data): # False:Public, True:Private
        if self.mode == 1:
            if "id" in data:
                id = data["id"]
                del data["id"]
            if type == False:
                server.send_message_to_all(json.dumps(data))
            elif type == True:
                server.send_message(id, json.dumps(data))

    def relayUserList(self, server, type, id):
        if self.mode == 1:
            y = ""
            for x in range(len(self.userlist)):
                y = str(y + self.userlist[x] + ";")
            self.sendPacket(server, type, {"cmd":"ulist", "id":id, "val":str(y)})

    def closedConnection(self, client, server):
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
                    self.relayUserList(server, False, client)

    def gotPacket(self, client, server, message):
        if self.mode == 1:
            err = False
            try:
                packet = json.loads(message)
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
                        
                        if cmd == "clear": # Clears comms
                            self.sendPacket(server, False, {"cmd":"gmsg", "val":""})
                            self.sendPacket(server, False, {"cmd":"pmsg", "val":""})
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
                                self.relayUserList(server, False, client)
                        if cmd == "gmsg": # Set global stream data values
                            self.gdata = str(val)
                            self.sendPacket(server, False, {"cmd":"gmsg", "val":self.gdata})
                        if cmd == "pmsg": # Set private stream data values
                            if not id == "":
                                self.sendPacket(server, True, {"cmd":"pmsg", "id":id, "val":val})
                        if cmd == "gvar": # Set global variable data values
                            self.sendPacket(server, False, {"cmd":"gvar", "name":name, "val":val})
                        if cmd == "pvar": # Set private variable data values
                            if not id == "":
                                self.sendPacket(server, True, {"cmd":"pvar", "name":name, "id":id, "val":val})

# This is the Frontend class, which handles the user interface when users run cloudlink.py directly.
class FrontEnd:
    def __init__(self):
        pass

    def clear(self):
        # for windows
        if name == 'nt':
            _ = system('cls')
        # for mac and linux(here, os.name is 'posix')
        else:
            _ = system('clear')

    def greeter(self):
        self.selectionMenu()

    def print_menu(self):
        self.clear()
        print("Welcome to CloudLink! Please select from the menu below.")
        print(30 * "-")
        if serverModeSupport and clientOrPluginModeSupport:
            print("1. Run in Server Mode")
            print("2. Run in Client Mode")
            print("3. Run in Plugin Mode")
            print("4. View Help")
            print("5. Exit")
        else:
            if serverModeSupport:
                print("1. Run in Server Mode")
                print("2. View Help")
                print("3. Exit")
            elif clientOrPluginModeSupport:
                print("1. Run in Client Mode")
                print("2. Run in Plugin Mode")
                print("3. View Help")
                print("4. Exit")
        
        print(30 * "-")

    def runServer(self):
        self.loop1 = True
        while self.loop1:
            try:
                self.port = int(input("Please enter the port number to run CloudLink Server on: "))
                self.loop1 = False
            except ValueError:
                print("Sorry, but that wasn't a number. Please try again.")
            except KeyboardInterrupt:
                print("\nGoodbye!")
                sys.exit()
        print("Press CTRL+C to exit.")
        cl = CloudLink()
        cl.host(self.port)
        input("Press enter to continue...")

    def runClient(self):
        input("This menu is a work in progress! Press enter to continue...")

    def runPlugin(self):
        input("This menu is a work in progress! Press enter to continue...")

    def runHelp(self):
        input("The Help menu is a work in progress! Press enter to continue...")

    def selectionMenu(self):
        self.loop = True       
        while self.loop:
            self.print_menu()
            try:
                self.choice = int(input("Enter your choice: "))
                if self.choice == 1:
                    if serverModeSupport and clientOrPluginModeSupport:
                        self.runServer()
                    else:
                        if serverModeSupport:
                            self.runServer()
                        elif clientOrPluginModeSupport:
                            self.runClient()
                elif self.choice == 2:
                    if (serverModeSupport and clientOrPluginModeSupport):
                        self.runClient()
                    else:
                        if serverModeSupport:
                            self.runHelp()
                        elif clientOrPluginModeSupport:
                            self.runPlugin()
                elif self.choice == 3:
                    if (serverModeSupport and clientOrPluginModeSupport):
                        self.runPlugin()
                    else:
                        if serverModeSupport:
                            self.loop = False
                            print("Goodbye!")
                            sys.exit()
                        elif clientOrPluginModeSupport:
                            self.runHelp()
                elif self.choice == 4:
                    if serverModeSupport and clientOrPluginModeSupport:
                        self.runHelp()
                    else:
                        if serverModeSupport:
                            input("That selection wasn't between 1-3. Press enter to continue...")
                        elif clientOrPluginModeSupport:
                            self.loop = False
                            print("Goodbye!")
                            sys.exit()
                elif self.choice == 5:
                    if serverModeSupport and clientOrPluginModeSupport:
                        self.loop = False
                        print("Goodbye!")
                        sys.exit()
                    else:
                        if serverModeSupport:
                            input("That selection wasn't between 1-3. Press enter to continue...")
                        elif clientOrPluginModeSupport:
                            input("That selection wasn't between 1-4. Press enter to continue...")
                else:
                    input("That selection isn't valid. Press enter to continue...")
            except ValueError:
                input("That wasn't a number. Press enter to continue...")

if __name__ == "__main__":
    if (not serverModeSupport) and (not clientOrPluginModeSupport):
        input("Press enter to continue... ")
        sys.exit()
    else:
        if (not serverModeSupport) or (not clientOrPluginModeSupport):
            input("Press enter to continue... ")
        fe = FrontEnd()
        fe.greeter()
