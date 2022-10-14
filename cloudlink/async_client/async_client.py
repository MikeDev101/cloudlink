import websockets
import asyncio
import json
from copy import copy
import time
import threading

# Multi client
class multi_client:
    def __init__(self, parent, logs:bool = True):
        self.shutdown_flag = False
        self.threads = set()
        self.logs = logs
        self.parent = parent

        self.clients_counter = int()
        self.clients_present = set()
        self.clients_dead = set()
    
    async def __on_connect__(self, client):
        self.clients_present.add(client)
        self.clients_dead.discard(client)
        while not self.shutdown_flag:
            await client.asyncio.sleep(0)
        await client.shutdown()

    async def __on_disconnect__(self, client):
        self.clients_present.discard(client)
        self.clients_dead.add(client)
    
    def spawn(self, id:any, url:str = "ws://127.0.0.1:3000/"):
        _client = client(self.parent, logs = self.logs)
        _client.obj_id = id
        _client.bind_event(_client.events.on_connect, self.__on_connect__)
        _client.bind_event(_client.events.on_close, self.__on_disconnect__)
        _client.bind_event(_client.events.on_fail, self.__on_disconnect__)
        self.threads.add(threading.Thread(
            target=_client.run,
            args=[url],
            daemon=True
        ))
        self.clients_counter = len(self.threads)
        return _client
    
    def run(self):
        for thread in self.threads:
            thread.start()
        while (len(self.clients_present) + len(self.clients_dead)) != self.clients_counter:
            print(f"{(len(self.clients_present) + len(self.clients_dead))} / {self.clients_counter}...", end="\r")
    
    def stop(self):
        self.shutdown_flag = True
        self.clients_counter = self.clients_counter - len(self.clients_dead)
        while len(self.clients_present) != 0:
            print(f"{len(self.clients_present)} / {self.clients_counter}...", end="\r")
        self.clients_present.clear()
        self.clients_dead.clear()
        self.threads.clear()

# Cloudlink Client
class client:
    def __init__(self, parent, logs:bool = True):
        self.version = parent.version

        # Locally define the client object
        self.client = None

        # Declare loop
        self.loop = None

        # Initialize required libraries
        self.asyncio = asyncio
        
        self.websockets = websockets
        self.copy = copy
        self.json = json
        
        # Other
        self.enable_logs = logs
        self.client_id = dict()
        self.client_ip = str()
        self.running = False
        self.username_set = False
        
        # Built-in listeners
        self.handshake_listener = "protocolset"
        self.setid_listener = "usernameset"
        self.ping_listener = "ping"
        
        # Storage of server stuff
        self.motd_message = str()
        self.server_version = str()
        
        # Managing methods
        self.custom_methods = custom_methods()
        self.events = events()
        self.disabled_methods = set()
        self.method_callbacks = dict()
        self.listener_callbacks = dict()
        
        # Initialize supporter
        self.supporter = parent.supporter(self)
        
        # Initialize attributes from supporter component
        self.log = self.supporter.log
        self.validate = self.supporter.validate
        self.load_custom_methods = self.supporter.load_custom_methods
        self.detect_listener = self.supporter.detect_listener
        self.generate_statuscode = self.supporter.generate_statuscode
        
        # Initialize rooms storage
        self.rooms = rooms(self)
        
        # Initialize methods
        self.cl_methods = cl_methods(self)
    
    # API basics
    
    def run(self, ip:str = "ws://127.0.0.1:3000/"):
        try:
            self.loop = self.asyncio.new_event_loop()
            self.asyncio.run(self.__session__(ip))
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(self.supporter.full_stack())
    
    async def shutdown(self):
        if not self.client:
            return
        
        if not self.client.open:
            return
        
        await self.client.close()

    async def send_raw_packet(self, packet:dict):
        if not self.client:
          return
        if not self.client.open:
            return
        await self.client.send(json.dumps(packet))
  
    async def send_packet (self, cmd:str, val:any = None, listener_detected:bool = False, listener_id:str = None, room_id:str = None, quirk:str = "quirk_embed_val"):
        if not self.client:
            return
        
        if not self.client.open:
            return

        # Manage specific message quirks
        message = {"cmd": cmd}
        if val:
            if quirk == self.supporter.quirk_update_msg:
                message.update(val)
            elif quirk == self.supporter.quirk_embed_val:
                message["val"] = val
            else:
                raise TypeError("Unknown message quirk!")

        # Attach a listener request
        if listener_detected:
            message["listener"] = listener_id
        
        # Attach the rooms key
        if room_id:
            message["rooms"] = room_id

        # Send payload
        try:
            await self.client.send(self.json.dumps(message))
        except self.websockets.exceptions.ConnectionClosedError:
            self.log(f"Failed to send packet: Connection closed unexpectedly")

    # API requests
    
    # Sets the client's username and enables pmsg, pvar, direct, and link/unlink commands.
    async def set_username(self, username):
        if not self.client:
            return

        if not self.client.open:
            return
        
        if self.username_set:
            return
        
        await self.send_packet(cmd = "setid", val = username, listener_detected = True, listener_id = self.setid_listener, quirk = self.supporter.quirk_embed_val)
    
    # Gives a ping, gets a pong. Keeps connections alive and healthy. This is recommended for servers with tunnels/reverse proxies that have connection timeouts.
    async def ping(self, listener:any = None):
        if not self.client:
            return
        
        if not self.client.open:
            return
        
        await self.send_packet(cmd = "ping", listener_detected = True, listener_id = self.ping_listener)
    
    # Sends global message packets.
    async def send_gmsg(self, value, listener:any = None):
        if not self.client:
            return
        
        if not self.client.open:
            return
        
        if listener:
            await self.send_packet(cmd = "gmsg", val = value, listener_detected = True, listener_id = listener, quirk = self.supporter.quirk_embed_val)
        else:
            await self.send_packet(cmd = "gmsg", val = value, quirk = self.supporter.quirk_embed_val)
    
    # Sends global variable packets. This will sync with all Scratch cloud variables.
    async def send_gvar(self, name, value, listener:any = None):
        if not self.client:
            return
        
        if not self.client.open:
            return
        
        payload = {
            "name": name,
            "val": value
        }
        
        if listener:
            await self.send_packet(cmd = "gvar", val = payload, listener_detected = True, listener_id = listener, quirk = self.supporter.quirk_update_msg)
        else:
            await self.send_packet(cmd = "gvar", val = payload, quirk = self.supporter.quirk_update_msg)
    
    # API callback utilities
    
    def bind_callback_method(self, callback_method:type, function:type):
        if hasattr(self.cl_methods, callback_method.__name__) or hasattr(self.custom_methods, callback_method.__name__):
            if not callback_method.__name__ in self.method_callbacks:
                self.method_callbacks[callback_method.__name__] = set()
            self.method_callbacks[callback_method.__name__].add(function)
    
    def bind_callback_listener(self, listener_str:str, function:type):
        if not listener_str in self.listener_callbacks:
            self.listener_callbacks[listener_str] = set()
        self.listener_callbacks[listener_str].add(function)

    def bind_event(self, event_method:type, function:type):
        if hasattr(self.events, event_method.__name__):
            if not event_method.__name__ in self.method_callbacks:
                self.method_callbacks[event_method.__name__] = set()
            self.method_callbacks[event_method.__name__].add(function)

    # Callback management

    def __fire_method_callbacks__(self, callback_method, message, listener_detected, listener_id):
        if callback_method.__name__ in self.method_callbacks:
            for _method in self.method_callbacks[callback_method.__name__]:
                self.asyncio.create_task(_method(self, message, listener_detected, listener_id))
    
    def __fire_method_listeners__(self, listener_str, message):
        if listener_str in self.listener_callbacks:
            for _method in self.listener_callbacks[listener_str]:
                self.asyncio.create_task(_method(self, message))

    def __fire_event__(self, event_method:type):
        if event_method.__name__ in self.method_callbacks:
            for _method in self.method_callbacks[event_method.__name__]:
                self.asyncio.create_task(_method(self))
    
    # Connection management
    
    async def __method_handler__(self, message):
        # Check if the message contains the cmd key, with a string datatype.
        if self.validate({"cmd": str}, message) != self.supporter.valid:
            return

        # Detect listeners
        listener_detected, listener_id = self.detect_listener(message)

        # Detect and convert CLPv3 custom responses to CLPv4
        if (message["cmd"] == "direct") and ("val" in message):
            if self.validate({"cmd": str, "val": self.supporter.keydefaults["val"]}, message["val"]) == self.supporter.valid:
                tmp_msg = {
                    "cmd": message["val"]["cmd"],
                    "val": message["val"]["val"]
                }
                message = self.copy(tmp_msg)

        # Check if the command is disabled
        if message["cmd"] in self.disabled_methods:
            return

        method = None
        
        # Check if the command method exists
        if hasattr(self.cl_methods, message["cmd"]):
            method = getattr(self.cl_methods, message["cmd"])
        
        elif hasattr(self.custom_methods, message["cmd"]):
            method = getattr(self.custom_methods, message["cmd"])

        if method:
            # Run the method
            await method(message, listener_detected, listener_id)
    
    async def __session__(self, ip):
        try:
            async with self.websockets.connect(ip) as self.client:
                await self.send_packet(cmd = "handshake", listener_detected = True, listener_id = self.handshake_listener)
                try:
                    while self.client.open:
                        try:
                            message = json.loads(await self.client.recv())
                            await self.__method_handler__(message)
                        except Exception as e:
                            pass
                            #print(f"Connection handler error: {e}")
                finally:
                    self.__fire_event__(self.events.on_close)
        except Exception as e:
            self.log(f"Closing connection handler due to error: {e}")
            self.__fire_event__(self.events.on_fail)
        finally:
            pass

# Class for binding events
class events:
    def __init__(self):
        pass
    
    def on_connect(self):
        pass

    def on_error(self):
        pass

    def on_close(self):
        pass
    
    def on_fail(self):
        pass
    
    def on_username_set(self):
        pass
    
    def on_pong(self):
        pass

# Class for managing the Cloudlink Protocol
class cl_methods:
    def __init__(self, parent):
        self.parent = parent
        self.supporter = parent.supporter
        self.copy = parent.copy
        self.rooms = parent.rooms
        self.log = parent.log
        self.loop = None
    
    async def gmsg(self, message, listener_detected, listener_id):
        room_data = None
        if "rooms" in message:
            # Automatically create room and update the global data value
            self.rooms.create(message["rooms"]) 
            room_data = self.rooms.get(message["rooms"])
        else:
            # Assume a gmsg with no "rooms" value is the default room
            room_data = self.rooms.get("default")
        
        # Update the room data
        room_data.global_data_value = message["val"]
        
        # Fire callbacks for method and it's listener
        self.parent.__fire_method_callbacks__(self.gmsg, message, listener_detected, listener_id)
        if listener_detected:
            self.parent.__fire_method_listeners__(listener_id)
    
    async def pmsg(self, message, listener_detected, listener_id):
        room_data = None
        if "rooms" in message:
            # Automatically create room and update the global data value
            self.rooms.create(message["rooms"]) 
            room_data = self.rooms.get(message["rooms"])
        else:
            # Assume a gmsg with no "rooms" value is the default room
            room_data = self.rooms.get("default")
        
        # Update the room data
        room_data.private_data_value["val"] = message["val"]
        room_data.private_data_value["origin"] = message["origin"]
        
        # Fire callbacks for method and it's listener
        self.parent.__fire_method_callbacks__(self.pmsg, message, listener_detected, listener_id)
        if listener_detected:
            self.parent.__fire_method_listeners__(listener_id)
    
    async def gvar(self, message, listener_detected, listener_id):
        room_data = None
        if "rooms" in message:
            # Automatically create room and update the global data value
            self.rooms.create(message["rooms"]) 
            room_data = self.rooms.get(message["rooms"])
        else:
            # Assume a gmsg with no "rooms" value is the default room
            room_data = self.rooms.get("default")
        
        # Update the room data
        room_data.global_vars[message["name"]] = message["val"]
        
        # Fire callbacks for method and it's listener
        self.parent.__fire_method_callbacks__(self.gvar, message, listener_detected, listener_id)
        if listener_detected:
            self.parent.__fire_method_listeners__(listener_id)
    
    async def pvar(self, message, listener_detected, listener_id):
        room_data = None
        if "rooms" in message:
            # Automatically create room and update the global data value
            self.rooms.create(message["rooms"]) 
            room_data = self.rooms.get(message["rooms"])
        else:
            # Assume a gmsg with no "rooms" value is the default room
            room_data = self.rooms.get("default")
        
        # Update the room data
        room_data.private_vars[message["name"]] = {
            "origin": message["origin"],
            "val": message["val"]
        }
        
        # Fire callbacks for method and it's listener
        self.parent.__fire_method_callbacks__(self.pvar, message, listener_detected, listener_id)
        if listener_detected:
            self.parent.__fire_method_listeners__(listener_id)
    
    async def direct(self, message, listener_detected, listener_id):
        # Fire callbacks for method and it's listener
        self.parent.__fire_method_callbacks__(self.direct, message, listener_detected, listener_id)
        if listener_detected:
            self.parent.__fire_method_listeners__(listener_id)
    
    async def ulist(self, message, listener_detected, listener_id):
        room_data = None
        if "rooms" in message:
            # Automatically create room and update the global data value
            self.rooms.create(message["rooms"]) 
            room_data = self.rooms.get(message["rooms"])
        else:
            # Assume a gmsg with no "rooms" value is the default room
            room_data = self.rooms.get("default")
        
        # Interpret and execute ulist method
        if "mode" in message:
            if message["mode"] in ["set", "add", "remove"]:
                match message["mode"]:
                    case "set":
                        room_data.userlist = message["val"]
                    case "add":
                        if not message["val"] in room_data.userlist:
                            room_data.userlist.append(message["val"])
                    case "remove":
                        if message["val"] in room_data.userlist:
                            room_data.userlist.remove(message["val"])
            else:
                self.log(f"Could not understand ulist method: {message['mode']}")
        else:
            # Assume old userlist method
            room_data.userlist = set(message["val"])
        
        # ulist will never return a listener
        self.parent.__fire_method_callbacks__(self.ulist, message, listener_detected, listener_id)
    
    async def server_version(self, message, listener_detected, listener_id):
        self.parent.server_version = message['val']
        
        # server_version will never return a listener
        self.parent.__fire_method_callbacks__(self.server_version, message, listener_detected, listener_id)
    
    async def motd(self, message, listener_detected, listener_id):
        self.parent.motd_message = message['val']

        # motd will never return a listener
        self.parent.__fire_method_callbacks__(self.motd, message, listener_detected, listener_id)
    
    async def client_ip(self, message, listener_detected, listener_id):
        self.parent.client_ip = message['val']
        
        # client_ip will never return a listener
        self.parent.__fire_method_callbacks__(self.client_ip, message, listener_detected, listener_id)
    
    async def statuscode(self, message, listener_detected, listener_id):
        if listener_detected:
            if listener_id in [self.parent.handshake_listener, self.parent.setid_listener]:
                human_ok, machine_ok = self.supporter.generate_statuscode("OK")
                match listener_id:
                    case self.parent.handshake_listener:
                        if (message["code"] == human_ok) or (message["code_id"] == machine_ok):
                            self.parent.__fire_event__(self.parent.events.on_connect)
                        else:
                            await self.parent.shutdown()
                    case self.parent.setid_listener:
                        if (message["code"] == human_ok) or (message["code_id"] == machine_ok):
                            self.parent.username_set = True
                            self.parent.client_id = message["val"]
                            self.parent.__fire_event__(self.parent.events.on_username_set)
                    case self.parent.ping_listener:
                        self.parent.__fire_event__(self.parent.events.on_pong)
            else:
                self.parent.__fire_method_callbacks__(self.statuscode, message, listener_detected, listener_id)
                self.parent.__fire_method_listeners__(listener_id)
        else:
            self.parent.__fire_method_callbacks__(self.statuscode, message, listener_detected, listener_id)

# Class to store custom methods
class custom_methods:
    def __init__(self):
        pass

# Class to store room data
class rooms:
    def __init__(self, parent):
        self.default = self.__room__()
        self.__parent__ = parent
    
    def get_all(self):
        tmp = self.__parent__.copy(self.__dict__)

        # Remove attributes that aren't client objects
        del tmp["__parent__"]

        return tmp

    def exists(self, room_id:str):
        return hasattr(self, str(room_id))
    
    def create(self, room_id:str):
        if not self.exists(str(room_id)):
            setattr(self, str(room_id), self.__room__())
    
    def delete(self, room_id:str):
        if self.exists(str(room_id)):
            delattr(self, str(room_id))

    def get(self, room_id:str):
        if self.exists(str(room_id)):
            return getattr(self, str(room_id))
        else:
            return None

    class __room__:
        def __init__(self):
            # Global data stream current value
            self.global_data_value = str()
            
            # Private data stream current value
            self.private_data_value = {
                "origin": str(),
                "val": None
            }

            # Storage of all global variables / Scratch Cloud Variables
            self.global_vars = dict()

            # Storage of all private variables
            self.private_vars = dict()

            # User management
            self.userlist = list()