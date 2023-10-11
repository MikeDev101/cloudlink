#!/usr/bin/env python3

version = "0.1.7"

# Server based on https://github.com/Pithikos/python-websocket-server
# Client based on https://github.com/websocket-client/websocket-client

"""
CloudLink by MikeDEV
Please see https://github.com/MikeDev101/cloudlink for more details.

0BSD License
Copyright (C) 2020-2022 MikeDEV Software, Co.
Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted.
THE SOFTWARE IS PROVIDED “AS IS” AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
"""

import json
import sys
import threading
from websocket_server import WebsocketServer as ws_server
import websocket as ws_client

"""
Code formatting

(Type):(Code) | (Description)

Type: Letter
    I - Info
    E - Error

Code: Number, defines the code

Description: String, Describes the code
"""

class API:
    def server(self, ip="127.0.0.1", port=3000, threaded=False): # Runs CloudLink in server mode.
        try:
            if self.state == 0:
                # Change the link state to 1 (Server mode)
                self.state = 1
                self.wss = ws_server(
                    host=ip,
                    port=port
                )
                
                # Set the server's callbacks to CloudLink's class functions
                self.wss.set_fn_new_client(self._on_connection_server)
                self.wss.set_fn_client_left(self._closed_connection_server)
                self.wss.set_fn_message_received(self._on_packet_server)
                
                # Format dict for storing this mode's specific data
                
                if (not "motd" in self.statedata) or (not "motd_enable" in self.statedata):
                    self.statedata["motd_enable"] = False
                    self.statedata["motd"] = ""
                if (not "secure_enable" in self.statedata) or (not "secure_keys" in self.statedata):
                    self.statedata["secure_enable"] = False
                    self.statedata["secure_keys"] = []
                self.statedata = {
                    "ulist": {
                        "usernames": {},
                        "objs": {}
                    }, # Username list for the "Usernames" block
                    "secure_enable": False, # Trusted Access enabler
                    "secure_keys": [], # Trusted Access keys
                    "gmsg": "", # Global data stream
                    "motd_enable": self.statedata["motd_enable"], # MOTD enabler
                    "motd": self.statedata["motd"], # MOTD text
                    "secure_enable": self.statedata["secure_enable"], # Trusted Access enabler
                    "secure_keys": self.statedata["secure_keys"] # Trusted Access keys
                }
                
                # Run the server
                print("Running server on ws://{0}:{1}/".format(ip, port))
                self.wss.run_forever(threaded=threaded)
            else:
                if self.debug:
                    print("Error: Attempted to switch states!")
        except Exception as e:
            if self.debug:
                print("Error at client: {0}".format(e))
    
    def client(self, ip="ws://127.0.0.1:3000/"): # Runs CloudLink in client mode.
        try:
            if self.state == 0:
                # Change the link state to 2 (Client mode)
                self.state = 2
                self.wss = ws_client.WebSocketApp(
                    ip,
                    on_message = self._on_packet_client,
                    on_error = self._on_error_client,
                    on_open = self._on_connection_client,
                    on_close = self._closed_connection_client
                )
                
                # Format dict for storing this mode's specific data
                self.statedata = {
                    "ulist": {
                        "usernames": []
                    },
                }
                
                # Run the client
                self.wss.run_forever()
            else:
                if self.debug:
                    print("Error: Attempted to switch states!")
        except Exception as e:
            if self.debug:
                print("Error at client: {0}".format(e))
    
    def stop(self, abrupt=False): # Stops CloudLink (not sure if working)
        try:
            if self.state == 1:
                if abrupt:
                    self.wss.shutdown_abruptly()
                else:
                    self.wss.shutdown_gracefully()
                self.state = 0
            elif self.state == 2:
                self.wss.close()
            else:
                if self.debug:
                    print("Error: Attempted to stop in an invalid mode")
        except Exception as e:
            if self.debug:
                print("Error at stop: {0}".format(e))
    
    def callback(self, callback_id, function): # Add user-friendly callbacks for CloudLink to be useful as a module
        try:
            if callback_id in self.callback_function:
                self.callback_function[callback_id] = function
                if self.debug:
                    print("Binded callback {0}.".format(callback_id))
            else:
                if self.debug:
                    print("Error: Callback {0} is not a valid callback id!".format(callback_id))
        except Exception as e:
            if self.debug:
                print("Error at callback: {0}".format(e))
    
    """
    def trustedAccess(self, enable, keys): #Feature NOT YET IMPLEMENTED
        if type(enable) == bool:
            if type(keys) == list:
                if enable:
                    if self.debug:
                        print("Enabled Trusted Access.")
                else:
                    if self.debug:
                        print("Disabled Trusted Access.")
                self.statedata["secure_enable"] = enable
                self.statedata["secure_keys"] = keys
            else:
                if self.debug:
                    print('Error: Cannot set Trusted Access keys: expecting <class "list">, got {0}'.format(type(enable)))
        else:
            if self.debug:
                print('Error: Cannot set Trusted Access enable: expecting <class "bool">, got {0}'.format(type(enable)))
    """
    
    def sendPacket(self, msg): # User-friendly message sender for both server and client.
        try:
            payload = json.dumps(msg)
            if self.state == 1:
                if ("id" in msg) and (type(msg["id"]) == str) and (msg["cmd"] not in ["gmsg", "gvar"]):
                    id = msg["id"]
                    if id in self.statedata["ulist"]["usernames"]:
                        try:
                            client = self.statedata["ulist"]["objs"][self.statedata["ulist"]["usernames"][id]]["object"]
                            if self.debug:
                                print('Sending {0} to {1}'.format(msg, id))
                            if self._get_client_type(client) == "scratch":
                                if ("val" in msg) and (type(msg["val"]) == dict):
                                    msg["val"] = json.dumps(msg["val"])
                            self.wss.send_message(client, json.dumps(msg))
                        except Exception as e:
                            if self.debug:
                                print("Error on sendPacket (server): {0}".format(e))
                else:
                    try:
                        if self.debug:
                            print('Sending "{0}" to all clients'.format(json.dumps(msg)))
                        self._send_to_all(json.dumps(msg))
                    except Exception as e:
                            if self.debug:
                                print("Error on sendPacket (server): {0}".format(e))
            elif self.state == 2:
                try:
                    if self.debug:
                        print('Sending {0}'.format(json.dumps(msg)))
                    self.wss.send(json.dumps(msg))
                except Exception as e:
                    if self.debug:
                        print("Error on sendPacket (client): {0}".format(e))
            else:
                print("Error: Cannot use the packet sender in current state!")
        except json.decoder.JSONDecodeError:
            print("Error: JSON dump error, refusing to send")
        except Exception as e:
            print("Error on sendPacket: {0}".format(e))
    
    def setMOTD(self, motd, enable=True): # Sets the MOTD on the server-side.
        try:
            if type(enable) == bool:
                if type(motd) == str:
                    if enable:
                        print('Set MOTD to "{0}".'.format(motd))
                        self.statedata["motd"] = str(motd)
                        self.statedata["motd_enable"] = True
                    else:
                        print("Disabled MOTD.")
                        self.statedata["motd"] = None
                        self.statedata["motd_enable"] = False
                else:
                    print('Error: Cannot set MOTD text: expecting <class "str">, got {0}'.format(type(enable)))
            else:
                print('Error: Cannot set the enabler for MOTD: expecting <class "bool">, got {0}'.format(type(enable)))
        except Exception as e:
            if self.debug:
                print("Error at setMOTD: {0}".format(e))

    def getUsernames(self): # Returns the username list.
        if self.state == 1:
            return list((self.statedata["ulist"]["usernames"]).keys())
        elif self.state == 2:
            return self.statedata["ulist"]["usernames"]
        else:
            return None
"""
class CLTLS: #Feature NOT YET IMPLEMENTED
    def __init__(self):
        pass
"""

"""
class CLTLS: #Feature NOT YET IMPLEMENTED
    def __init__(self):
        pass
"""

class CloudLink(API):
    def __init__(self, debug=False): # Initializes CloudLink
        self.wss = None # Websocket Object
        self.state = 0 # Module state
        self.userlist = [] # Stores usernames set on link
        self.callback_function = { # For linking external code, use with functions
            "on_connect": None, # Handles new connections (server) or when connected to a server (client)
            "on_error": None, # Error reporter
            "on_packet": None, # Packet handler
            "on_close": None # Runs code when disconnected (client) or server stops (server)
        }
        self.debug = debug # Print back specific data
        self.statedata = {} # Place to store other garbage for modes
        self.codes = { # Current set of CloudLink status/error self.codes
            "Test": "I:000 | Test", # Test code
            "OK": "I:100 | OK", # OK code
            "Syntax": "E:101 | Syntax",
            "Datatype": "E:102 | Datatype",
            "IDNotFound": "E:103 | ID not found",
            "InternalServerError": "E:104 | Internal",
            "Loop": "E:105 | Loop detected",
            "RateLimit": "E:106 | Too many requests",
            "TooLarge": "E:107 | Packet too large",
            "BrokenPipe": "E:108 | Broken pipe",
            "EmptyPacket": "E:109 | Empty packet",
            "IDConflict": "E:110 | ID conflict",
            "IDSet": "E:111 | ID already set",
            "TAEnabled": "I:112 | Trusted Access enabled",
            "TAInvalid": "E:113 | TA Key invalid",
            "TAExpired": "E:114 | TA Key expired",
            "Refused": "E:115 | Refused",
            "IDRequired": "E:116 | Username required"
        }
        
        print("CloudLink v{0}".format(str(version))) # Report version number
        if self.debug:
            print("Debug enabled")
    
    def _is_json(self, data): # Checks if something is JSON
        if type(data) == dict:
            return True
        else:
            try:
                tmp = json.loads(data)
                return True
            except Exception as e:
                return False
    
    def _get_client_type(self, client): # Gets client types to help prevent errors
        if client["id"] in self.statedata["ulist"]["objs"]:
            return self.statedata["ulist"]["objs"][client["id"]]["type"]
        else:
            return None
    
    def _get_obj_of_username(self, client): # Helps mitigate packet spoofing
        if client in self.statedata["ulist"]["usernames"]:
            return self.statedata["ulist"]["objs"][self.statedata["ulist"]["usernames"][client]]["object"]
        else:
            return None
    
    def _send_to_all(self, payload): # "Better" (?) send to all function
        tmp_payload = payload
        for client in self.wss.clients:
            #print("sending {0} to {1}".format(payload, client["id"]))
            if self._get_client_type(client) == "scratch":
                #print("sending to all, {0} is a scratcher".format(client["id"]))
                if ("val" in payload) and (type(payload["val"]) == dict):
                    #print("stringifying nested json")
                    tmp_payload["val"] = json.dumps(payload["val"])
                self.wss.send_message(client, json.dumps(tmp_payload))
            else:
                self.wss.send_message(client, json.dumps(payload))
    
    def _server_packet_handler(self, client, server, message): # The almighty packet handler, single-handedly responsible for over hundreds of lines of code
        if not len(str(message)) == 0:
            try:
                # Parse the JSON into a dict
                msg = json.loads(message)
                # Handle the packet
                if "cmd" in msg: # Verify that the packet contains the command parameter, which is needed to work.
                    if type(msg["cmd"]) == str:
                        if msg["cmd"] in ["gmsg", "pmsg", "setid", "direct", "gvar", "pvar"]:
                            if msg["cmd"] == "gmsg": # Handles global messages.
                                if "val" in msg: # Verify that the packet contains the required parameters.
                                    if self._get_client_type(client) == "scratch":
                                        if self._is_json(msg["val"]):
                                            msg["val"] = json.loads(msg["val"])
                                    if not len(str(msg["val"])) > 1000:
                                        if self.debug:
                                            print("message is {0} bytes".format(len(str(msg["val"]))))
                                        # Send the packet to all clients.
                                        self._send_to_all({"cmd": "gmsg", "val": msg["val"]})
                                        self.wss.send_message(client, json.dumps({"cmd": "statuscode", "val": self.codes["OK"]}))
                                    else:
                                        if self.debug:
                                            print('Error: Packet too large')
                                        self.wss.send_message(client, json.dumps({"cmd": "statuscode", "val": self.codes["TooLarge"]}))
                                else:
                                    if self.debug:
                                        print('Error: Packet missing parameters')
                                    self.wss.send_message(client, json.dumps({"cmd": "statuscode", "val": self.codes["Syntax"]}))
                            
                            if msg["cmd"] == "pmsg": # Handles private messages.
                                if ("val" in msg) and ("id" in msg): # Verify that the packet contains the required parameters.
                                    if self._get_client_type(client) == "scratch":
                                        if self._is_json(msg["val"]):
                                            msg["val"] = json.loads(msg["val"])
                                    if msg["id"] in self.statedata["ulist"]["usernames"]:
                                        if not len(str(msg["val"])) > 1000:
                                            if not client == self._get_obj_of_username(msg["id"]):
                                                try:
                                                    otherclient = self._get_obj_of_username(msg["id"])
                                                    if not len(str(self.statedata["ulist"]["objs"][client["id"]]["username"])) == 0:
                                                        msg["origin"] = self.statedata["ulist"]["objs"][client["id"]]["username"]
                                                        if (self._get_client_type(otherclient) == "scratch") and (self._is_json(msg["val"])):
                                                            tmp_val = json.dumps(msg["val"])
                                                        else:
                                                            tmp_val = msg["val"]
                                                        
                                                        if self.debug:
                                                            print('Sending {0} to {1}'.format(msg, msg["id"]))
                                                        del msg["id"]
                                                        self.wss.send_message(otherclient, json.dumps({"cmd": "pmsg", "val": tmp_val, "origin": msg["origin"]}))
                                                        self.wss.send_message(client, json.dumps({"cmd": "statuscode", "val": self.codes["OK"]}))
                                                    else:
                                                        self.wss.send_message(client, json.dumps({"cmd": "statuscode", "val": self.codes["IDRequired"]}))
                                                except Exception as e:
                                                    if self.debug:
                                                        print("Error on _server_packet_handler: {0}".format(e))
                                                        self.wss.send_message(client, json.dumps({"cmd": "statuscode", "val": self.codes["InternalServerError"]}))
                                            else:
                                                if self.debug:
                                                    print('Error: Potential packet loop detected, aborting')
                                                self.wss.send_message(client, json.dumps({"cmd": "statuscode", "val": self.codes["Loop"]}))
                                        else:
                                            if self.debug:
                                                print('Error: Packet too large')
                                            self.wss.send_message(client, json.dumps({"cmd": "statuscode", "val": self.codes["TooLarge"]}))
                                    else:
                                        if self.debug:
                                            print('Error: ID Not found')
                                        self.wss.send_message(client, json.dumps({"cmd": "statuscode", "val": self.codes["IDNotFound"]}))
                                else:
                                    if self.debug:
                                        print('Error: Packet missing parameters')
                                    self.wss.send_message(client, json.dumps({"cmd": "statuscode", "val": self.codes["Syntax"]}))
                            
                            if msg["cmd"] == "setid": # Sets the username of the client.
                                if "val" in msg: # Verify that the packet contains the required parameters.
                                    if not len(str(msg["val"])) == 0:
                                        if not len(str(msg["val"])) > 1000:
                                            if type(msg["val"]) == str:
                                                if self.statedata["ulist"]["objs"][client['id']]["username"] == "":
                                                    if not msg["val"] in self.statedata["ulist"]["usernames"]:
                                                        # Add the username to the list
                                                        self.statedata["ulist"]["usernames"][msg["val"]] = client["id"]
                                                        # Set the object's username info
                                                        self.statedata["ulist"]["objs"][client['id']]["username"] = msg["val"]
                                                        self.wss.send_message(client, json.dumps({"cmd": "statuscode", "val": self.codes["OK"]}))
                                                        self._send_to_all({"cmd": "ulist", "val": self._get_ulist()})
                                                        if self.debug:
                                                            print("User {0} set username: {1}".format(client["id"], msg["val"]))
                                                    else:
                                                        if self.debug:
                                                            print('Error: Refusing to set username because it would cause a conflict')
                                                        self.wss.send_message(client, json.dumps({"cmd": "statuscode", "val": self.codes["IDConflict"]}))
                                                else:
                                                    if self.debug:
                                                        print('Error: Refusing to set username because username has already been set')
                                                    self.wss.send_message(client, json.dumps({"cmd": "statuscode", "val": self.codes["IDSet"]}))
                                            else:
                                                if self.debug:
                                                    print('Error: Packet "val" datatype invalid: expecting <class "str">, got {0}'.format(type(msg["cmd"])))
                                                self.wss.send_message(client, json.dumps({"cmd": "statuscode", "val": self.codes["Datatype"]}))
                                        else:
                                            if self.debug:
                                                print('Error: Packet too large')
                                            self.wss.send_message(client, json.dumps({"cmd": "statuscode", "val": self.codes["TooLarge"]}))
                                    else:
                                        if self.debug:
                                            print("Error: Packet is empty")
                                        self.wss.send_message(client, json.dumps({"cmd": "statuscode", "val": self.codes["EmptyPacket"]}))
                                else:
                                    if self.debug:
                                        print('Error: Packet missing parameters')
                                    self.wss.send_message(client, json.dumps({"cmd": "statuscode", "val": self.codes["Syntax"]}))
                            
                            if msg["cmd"] == "direct": # Direct packet handler for server.
                                if self._get_client_type(client) == "scratch":
                                    if self._is_json(msg["val"]):
                                        msg["val"] = json.loads(msg["val"])
                                if ("val" in msg):
                                    if not self.callback_function["on_packet"] == None:
                                        if ("cmd" in msg["val"]) and (msg["val"]["cmd"] in ["type"]):
                                            if msg["val"]["cmd"] == "type":
                                                if "val" in msg["val"]:
                                                    self.statedata["ulist"]["objs"][client["id"]]["type"] = msg["val"]["val"] # Set the client type
                                                    if self.debug:
                                                        if msg["val"]["val"] == "scratch":
                                                            print("Client {0} is a CloudLink Scratch-based client type, will be stringfifying nested JSON".format(client["id"]))
                                                        elif msg["val"]["val"] == "py":
                                                            print("Client {0} is a CloudLink Python client type, will not be stringfifying nested JSON".format(client["id"]))
                                                        elif msg["val"]["val"] == "js":
                                                            print("Client {0} is a CloudLink JS client type, will not be stringfifying nested JSON".format(client["id"]))
                                                        else:
                                                            print("Client {0} is of unknown client type, claims it's {1}, assuming we do not need to be stringfifying nested JSON".format(client["id"], (msg["val"]["val"])))
                                                else:
                                                    if self.debug:
                                                        print('Error: Packet missing parameters')
                                                    self.wss.send_message(client, json.dumps({"cmd": "statuscode", "val": self.codes["Syntax"]}))
                                            else:
                                                self.wss.send_message(client, json.dumps({"cmd": "statuscode", "val": self.codes["OK"]}))
                                        elif not len(str(self.statedata["ulist"]["objs"][client["id"]]["username"])) == 0:
                                            origin = self.statedata["ulist"]["objs"][client["id"]]["username"]
                                            if self.debug:
                                                print("Handling direct command from {0}".format(origin))
                                            self.callback_function["on_packet"]({"val": msg["val"], "id": origin})
                                        else:
                                            self.wss.send_message(client, json.dumps({"cmd": "statuscode", "val": self.codes["IDRequired"]}))
                                else:
                                    if self.debug:
                                        print('Error: Packet missing parameters')
                                    self.wss.send_message(client, json.dumps({"cmd": "statuscode", "val": self.codes["Syntax"]}))
                            
                            if msg["cmd"] == "gvar": # Handles global variables.
                                if ("val" in msg) and ("name" in msg): # Verify that the packet contains the required parameters.
                                    if self._get_client_type(client) == "scratch":
                                        if self._is_json(msg["val"]):
                                            msg["val"] = json.loads(msg["val"])
                                    if (not len(str(msg["val"])) > 1000) and (not len(str(msg["name"])) > 100):
                                        # Send the packet to all clients.
                                        self._send_to_all({"cmd": "gvar", "val": msg["val"], "name": msg["name"]})
                                        self.wss.send_message(client, json.dumps({"cmd": "statuscode", "val": self.codes["OK"]}))
                                    else:
                                        if self.debug:
                                            print('Error: Packet too large')
                                        self.wss.send_message(client, json.dumps({"cmd": "statuscode", "val": self.codes["TooLarge"]}))
                                else:
                                    if self.debug:
                                        print('Error: Packet missing parameters')
                                    self.wss.send_message(client, json.dumps({"cmd": "statuscode", "val": self.codes["Syntax"]}))
                            
                            if msg["cmd"] == "pvar": # Handles private variables.
                                if ("val" in msg) and ("id" in msg) and ("name" in msg): # Verify that the packet contains the required parameters.
                                    if self._get_client_type(client) == "scratch":
                                        if self._is_json(msg["val"]):
                                            msg["val"] = json.loads(msg["val"])
                                    if msg["id"] in self.statedata["ulist"]["usernames"]:
                                        if (not len(str(msg["val"])) > 1000) and (not len(str(msg["name"])) > 1000):
                                            if not client == self._get_obj_of_username(msg["id"]):
                                                try:
                                                    otherclient = self._get_obj_of_username(msg["id"])
                                                    if not len(str(self.statedata["ulist"]["objs"][client["id"]]["username"])) == 0:
                                                        msg["origin"] = self.statedata["ulist"]["objs"][client["id"]]["username"]
                                                        if (self._get_client_type(otherclient) == "scratch") and ((self._is_json(msg["val"])) or (type(msg["val"]) == dict)):
                                                            tmp_val = json.dumps(msg["val"])
                                                        else:
                                                            tmp_val = msg["val"]
                                                        if self.debug:
                                                            print('Sending {0} to {1}'.format(msg, msg["id"]))
                                                        del msg["id"]
                                                        self.wss.send_message(otherclient, json.dumps({"cmd": "pvar", "val": tmp_val, "name": msg["name"], "origin": msg["origin"]}))
                                                        self.wss.send_message(client, json.dumps({"cmd": "statuscode", "val": self.codes["OK"]}))
                                                    else:
                                                        self.wss.send_message(client, json.dumps({"cmd": "statuscode", "val": self.codes["IDRequired"]}))
                                                except Exception as e:
                                                    if self.debug:
                                                        print("Error on _server_packet_handler: {0}".format(e))
                                                        self.wss.send_message(client, json.dumps({"cmd": "statuscode", "val": self.codes["InternalServerError"]}))
                                            else:
                                                if self.debug:
                                                    print('Error: Potential packet loop detected, aborting')
                                                self.wss.send_message(client, json.dumps({"cmd": "statuscode", "val": self.codes["Loop"]}))
                                        else:
                                            if self.debug:
                                                print('Error: Packet too large')
                                            self.wss.send_message(client, json.dumps({"cmd": "statuscode", "val": self.codes["TooLarge"]}))
                                    else:
                                        if self.debug:
                                            print('Error: ID Not found')
                                        self.wss.send_message(client, json.dumps({"cmd": "statuscode", "val": self.codes["IDNotFound"]}))
                                else:
                                    if self.debug:
                                        print('Error: Packet missing parameters')
                                    self.wss.send_message(client, json.dumps({"cmd": "statuscode", "val": self.codes["Syntax"]}))
                        
                        else: # Route the packet using UPL.
                            if ("val" in msg) and ("id" in msg): # Verify that the packet contains the required parameters.
                                if self._get_client_type(client) == "scratch":
                                    if self._is_json(msg["val"]):
                                        msg["val"] = json.loads(msg["val"])
                                if msg["id"] in self.statedata["ulist"]["usernames"]:
                                    if not len(str(msg["val"])) > 1000:
                                        if not client == self._get_obj_of_username(msg["id"]):
                                            try:
                                                otherclient = self._get_obj_of_username(msg["id"])
                                                if not len(str(self.statedata["ulist"]["objs"][client["id"]]["username"])) == 0:
                                                    msg["origin"] = self.statedata["ulist"]["objs"][client["id"]]["username"]
                                                    if (self._get_client_type(otherclient) == "scratch") and ((self._is_json(msg["val"])) or (type(msg["val"]) == dict)):
                                                        tmp_val = json.dumps(msg["val"])
                                                    else:
                                                        tmp_val = msg["val"]
                                                    
                                                    if self.debug:
                                                        print('Routing {0} to {1}'.format(msg, msg["id"]))
                                                    del msg["id"]
                                                    self.wss.send_message(otherclient, json.dumps(msg))
                                                    self.wss.send_message(client, json.dumps({"cmd": "statuscode", "val": self.codes["OK"]}))
                                                else:
                                                    self.wss.send_message(client, json.dumps({"cmd": "statuscode", "val": self.codes["IDRequired"]}))
                                            except Exception as e:
                                                if self.debug:
                                                    print("Error on _server_packet_handler: {0}".format(e))
                                                    self.wss.send_message(client, json.dumps({"cmd": "statuscode", "val": self.codes["InternalServerError"]}))
                                        else:
                                            if self.debug:
                                                print('Error: Potential packet loop detected, aborting')
                                            self.wss.send_message(client, json.dumps({"cmd": "statuscode", "val": self.codes["Loop"]}))
                                    else:
                                        if self.debug:
                                            print('Error: Packet too large')
                                        self.wss.send_message(client, json.dumps({"cmd": "statuscode", "val": self.codes["TooLarge"]}))
                                else:
                                    if self.debug:
                                        print('Error: ID Not found')
                                    self.wss.send_message(client, json.dumps({"cmd": "statuscode", "val": self.codes["IDNotFound"]}))
                            else:
                                if self.debug:
                                    print('Error: Packet missing parameters')
                                self.wss.send_message(client, json.dumps({"cmd": "statuscode", "val": self.codes["Syntax"]}))
                    else:
                        if self.debug:
                            print('Error: Packet "cmd" datatype invalid: expecting <class "bool">, got {0}'.format(type(msg["cmd"])))
                        self.wss.send_message(client, json.dumps({"cmd": "statuscode", "val": self.codes["Datatype"]}))
                else:
                    if self.debug:
                        print('Error: Packet missing "cmd" parameter')
                    self.wss.send_message(client, json.dumps({"cmd": "statuscode", "val": self.codes["Syntax"]}))
            except json.decoder.JSONDecodeError:
                if self.debug:
                    print("Error: Failed to parse JSON")
                self.wss.send_message(client, json.dumps({"cmd": "statuscode", "val": self.codes["Syntax"]}))
            except Exception as e:
                if self.debug:
                    print("Error on _server_packet_handler: {0}".format(e))
                self.wss.send_message(client, json.dumps({"cmd": "statuscode", "val": self.codes["InternalServerError"]}))
        else:
            if self.debug:
                print("Error: Packet is empty")
            self.wss.send_message(client, json.dumps({"cmd": "statuscode", "val": self.codes["EmptyPacket"]}))
    
    def _get_ulist(self): # Generates username list
        tmp_ulist = list((self.statedata["ulist"]["usernames"]).keys())
        for item in tmp_ulist:
            if item[0] == "%" and item[len(item)-1] == "%":
                tmp_ulist.pop(tmp_ulist.index(item))
        
        output = ""
        for item in tmp_ulist:
            output = output + item + ";"
        return output
    
    def _on_connection_server(self, client, server): # Server-side new connection handler
        try:
            if self.debug:
                print("New connection: {0}".format(str(client['id'])))
            
            # Add the client to the ulist object in memory.
            self.statedata["ulist"]["objs"][client["id"]] = {"object": client, "username": "", "ip": "", "type": ""}
            
            # Send the current username list.
            self.wss.send_message(client, json.dumps({"cmd": "ulist", "val": self._get_ulist()}))
            
            # Send the current global data stream value.
            self.wss.send_message(client, json.dumps({"cmd": "gmsg", "val": str(self.statedata["gmsg"])}))
            
            # Send the MOTD if enabled.
            if self.statedata["motd_enable"]:
                self.wss.send_message(client, json.dumps({"cmd": "direct", "val": {"cmd": "motd", "val": str(self.statedata["motd"])}}))
            
            # Send server version.
            self.wss.send_message(client, json.dumps({"cmd": "direct", "val": {"cmd": "vers", "val": str(version)}}))
            
            if not self.callback_function["on_connect"] == None:
                def run(*args):
                    try:
                        self.callback_function["on_connect"]()
                    except Exception as e:
                        if self.debug:
                            print("Error on _on_connection_server: {0}".format(e))
                        self.wss.send_message(client, json.dumps({"cmd": "statuscode", "val": self.codes["InternalServerError"]}))
                threading.Thread(target=run).start()
        except Exception as e:
            if self.debug:
                print("Error on _on_connection_server: {0}".format(e))
            self.wss.send_message(client, json.dumps({"cmd": "statuscode", "val": self.codes["InternalServerError"]}))
    
    def _closed_connection_server(self, client, server): # Server-side client closed connection handler
        try:
            if self.debug:
                if self.statedata["ulist"]["objs"][client['id']]["username"] == "":
                    print("Connection closed: {0}".format(str(client['id'])))
                else:
                    print("Connection closed: {0} ({1})".format(str(client['id']), str(self.statedata["ulist"]["objs"][client['id']]["username"])))
            
            # Remove entries from username list and userlist objects
            if self.statedata["ulist"]["objs"][client['id']]["username"] in self.statedata["ulist"]["usernames"]:
                del self.statedata["ulist"]["usernames"][self.statedata["ulist"]["objs"][client['id']]["username"]]
            del self.statedata["ulist"]["objs"][client['id']]
            
            self._send_to_all({"cmd": "ulist", "val": self._get_ulist()})
            if not self.callback_function["on_close"] == None:
                def run(*args):
                    try:
                        self.callback_function["on_close"]()
                    except Exception as e:
                        if self.debug:
                            print("Error on _closed_connection_server: {0}".format(e))
                threading.Thread(target=run).start()
        except Exception as e:
            if self.debug:
                print("Error on _closed_connection_server: {0}".format(e))
    
    def _on_packet_server(self, client, server, message): # Server-side new packet handler (Gives it's powers to _server_packet_handler)
        try:
            if self.debug:
                print("New packet from {0}: {1} bytes".format(str(client['id']), str(len(message))))
            def run(*args):
                try:
                    self._server_packet_handler(client, server, message)
                except Exception as e:
                    if self.debug:
                        print("Error on _on_packet_server: {0}".format(e))
                    self.wss.send_message(client, json.dumps({"cmd": "statuscode", "val": self.codes["InternalServerError"]}))
            threading.Thread(target=run).start()
        except Exception as e:
            if self.debug:
                print("Error on _on_packet_server: {0}".format(e))
            self.wss.send_message(client, json.dumps({"cmd": "statuscode", "val": self.codes["InternalServerError"]}))
    
    def _on_connection_client(self, ws): # Client-side connection handler
        try:
            if self.debug:
                print("Connected")
            self.wss.send(json.dumps({"cmd": "direct", "val": {"cmd": "type", "val": "py"}})) # Specify to the server that the client is based on Python
            if not self.callback_function["on_connect"] == None:
                def run(*args):
                    try:
                        self.callback_function["on_connect"]()
                    except Exception as e:
                        if self.debug:
                            print("Error on _on_connection_client: {0}".format(e))
                threading.Thread(target=run).start()
        except Exception as e:
            if self.debug:
                print("Error on _on_connection_client: {0}".format(e))
    
    def _on_packet_client(self, ws, message): # Client-side packet handler
        try:
            if self.debug:
                print("New packet: {0}".format(message))
            
            tmp = json.loads(message)
            if (("cmd" in tmp) and (tmp["cmd"] == "ulist")) and ("val" in tmp):
                self.statedata["ulist"]["usernames"] = str(tmp["val"]).split(";")
                del self.statedata["ulist"]["usernames"][len(self.statedata["ulist"]["usernames"])-1]
                if self.debug:
                    print("Username list:", str(self.statedata["ulist"]["usernames"]))
            
            if not self.callback_function["on_packet"] == None:
                def run(*args):
                    try:
                        self.callback_function["on_packet"](message)
                    except Exception as e:
                        if self.debug:
                            print("Error on _on_packet_client: {0}".format(e))
                threading.Thread(target=run).start()
        except Exception as e:
            if self.debug:
                print("Error on _on_packet_client: {0}".format(e))
    
    def _on_error_client(self, ws, error): # Client-side error handler
        try:
            if self.debug:
                print("Error: {0}".format(str(error)))
            if not self.callback_function["on_error"] == None:
                def run(*args):
                    try:
                        self.callback_function["on_error"](error)
                    except Exception as e:
                        if self.debug:
                            print("Error on _on_error_client: {0}".format(e))
                threading.Thread(target=run).start()
        except Exception as e:
            if self.debug:
                print("Error on _on_error_client: {0}".format(e))
    
    def _closed_connection_client(self, ws, close_status_code, close_msg): #Client-side closed connection handler
        try:
            if self.debug:
                print("Closed, status: {0} with code {1}".format(str(close_status_code), str(close_msg)))
            if not self.callback_function["on_close"] == None:
                def run(*args):
                    try:
                        self.callback_function["on_close"]()
                    except Exception as e:
                        if self.debug:
                            print("Error on _closed_connection_client: {0}".format(e))
                threading.Thread(target=run).start()
        except Exception as e:
            if self.debug:
                print("Error on _closed_connection_client: {0}".format(e))