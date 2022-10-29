import websocket as old_websockets
import json
from copy import copy
import time
import threading


# Multi client
class multi_client:
    def __init__(self, parent, logs: bool = True):
        self.shutdown_flag = False
        self.threads = set()
        self.logs = logs
        self.parent = parent

        self.clients_counter = int()
        self.clients_present = set()
        self.clients_dead = set()

    def on_connect(self, client):
        self.clients_present.add(client)
        self.clients_dead.discard(client)
        while not self.shutdown_flag:
            time.sleep(0)
        client.shutdown()

    def on_disconnect(self, client):
        self.clients_present.discard(client)
        self.clients_dead.add(client)

    def spawn(self, client_id: any, url: str = "ws://127.0.0.1:3000/"):
        _client = client(self.parent, logs=self.logs)
        _client.obj_id = client_id
        _client.bind_event(_client.events.on_connect, self.on_connect)
        _client.bind_event(_client.events.on_close, self.on_disconnect)
        _client.bind_event(_client.events.on_fail, self.on_disconnect)
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
    def __init__(self, parent, logs: bool = True):
        self.version = parent.version

        # Locally define the client object
        self.client = None

        self.websockets = old_websockets
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
        self.disabled_methods = set()
        self.method_callbacks = dict()
        self.listener_callbacks = dict()
        self.safe_methods = set()

        # Managing events
        self.events = events()
        self.event_callbacks = dict()

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

        # Load safe CLPv4 methods to mitigate vulnerabilities
        self.supporter.init_builtin_cl_methods()

    # == Public API functionality ==

    # Runs the client.
    def run(self, ip: str = "ws://127.0.0.1:3000/"):
        try:
            self.client = old_websockets.WebSocketApp(
                ip,
                on_message=self.__session_on_message__,
                on_error=self.__session_on_error__,
                on_open=self.__session_on_connect__,
                on_close=self.__session_on_close__
            )
            self.client.run_forever()
        except Exception as e:
            self.log(f"{e}: {self.supporter.full_stack()}")

    # Disconnects the client.
    def shutdown(self):
        if not self.client:
            return

        self.client.close()

    # Sends packets, you should use other methods.
    def send_packet(self, cmd: str, val: any = None, listener: str = None, room_id: str = None,
                    quirk: str = "quirk_embed_val"):
        if not self.client:
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
        if listener:
            message["listener"] = listener

        # Attach the rooms key
        if room_id:
            message["rooms"] = room_id

        # Send payload
        try:
            self.client.send(self.json.dumps(message))
        except Exception as e:
            self.log(f"Failed to send packet: {e}")

    # Sets the client's username and enables pmsg, pvar, direct, and link/unlink commands.
    def set_username(self, username):
        if not self.client:
            return

        if self.username_set:
            return

        self.send_packet(cmd="setid", val=username, listener=self.setid_listener, quirk=self.supporter.quirk_embed_val)

    # Gives a ping, gets a pong. Keeps connections alive and healthy. This is recommended for servers with tunnels/reverse proxies that have connection timeouts.
    def ping(self, listener: any = None):
        if not self.client:
            return

        if listener:
            self.send_packet(cmd="ping", listener=listener)
        else:
            self.send_packet(cmd="ping", listener=self.ping_listener)

    # Sends global message packets.
    def send_gmsg(self, value, listener: any = None):
        if not self.client:
            return

        if listener:
            self.send_packet(cmd="gmsg", val=value, listener=listener, quirk=self.supporter.quirk_embed_val)
        else:
            self.send_packet(cmd="gmsg", val=value, quirk=self.supporter.quirk_embed_val)

    # Sends global variable packets. This will sync with all Scratch cloud variables.
    def send_gvar(self, name, value, listener: any = None):
        if not self.client:
            return

        payload = {
            "name": name,
            "val": value
        }

        self.send_packet(cmd="gvar", val=payload, listener=listener, quirk=self.supporter.quirk_update_msg)

    # Sends private message packets.
    def send_pmsg(self, recipient, value, listener: any = None):
        if not self.client:
            return

        payload = {
            "id": recipient,
            "val": value
        }

        self.send_packet(cmd="pmsg", val=payload, listener=listener, quirk=self.supporter.quirk_update_msg)

    # Sends private variable packets. This does not sync with Scratch.
    def send_pvar(self, name, recipient, value, listener: any = None):
        if not self.client:
            return

        payload = {
            "name": name,
            "id": recipient,
            "val": value
        }

        self.send_packet(cmd="pvar", val=payload, listener=listener, quirk=self.supporter.quirk_update_msg)

    # Sends direct variable packets.
    def send_direct(self, recipient: any = None, value: any = None, listener: any = None):
        if not self.client:
            return

        payload = dict()
        if recipient:
            payload["id"] = recipient

        if value:
            payload.update(value)

        self.send_packet(cmd="direct", val=payload, listener=listener, quirk=self.supporter.quirk_update_msg)

    # Binding method callbacks - Provides a programmer-friendly interface to run extra code after a cloudlink method has been executed.
    def bind_callback_method(self, callback_method: type, function: type):
        if hasattr(self.cl_methods, callback_method.__name__) or hasattr(self.custom_methods, callback_method.__name__):
            if callback_method.__name__ not in self.method_callbacks:
                self.method_callbacks[callback_method.__name__] = set()
            self.method_callbacks[callback_method.__name__].add(function)

    # Binding listener callbacks - Provides a programmer-friendly interface to run extra code when a message listener was detected.
    def bind_callback_listener(self, listener_str: str, function: type):
        if listener_str not in self.listener_callbacks:
            self.listener_callbacks[listener_str] = set()
        self.listener_callbacks[listener_str].add(function)

    # Binding events - Provides a programmer-friendly interface to detect client connects, disconnects, and errors.
    def bind_event(self, event_method: type, function: type):
        if hasattr(self.events, event_method.__name__):
            if event_method.__name__ not in self.event_callbacks:
                self.event_callbacks[event_method.__name__] = set()
            self.event_callbacks[event_method.__name__].add(function)

    # == Client functionality ==

    def __fire_method_callbacks__(self, callback_method, message, listener):
        if callback_method.__name__ in self.method_callbacks:
            for _method in self.method_callbacks[callback_method.__name__]:
                threading.Thread(target=_method, args=[self, message, listener], daemon=True).start()

    def __fire_method_listeners__(self, listener_str, message):
        if listener_str in self.listener_callbacks:
            for _method in self.listener_callbacks[listener_str]:
                threading.Thread(target=_method, args=[self, message], daemon=True).start()

    def __fire_event__(self, event_method: type):
        if event_method.__name__ in self.event_callbacks:
            for _method in self.event_callbacks[event_method.__name__]:
                threading.Thread(target=_method, args=[self], daemon=True).start()

    def __method_handler__(self, message):
        # Check if the message contains the cmd key, with a string datatype.
        if self.validate({"cmd": str}, message) != self.supporter.valid:
            return

        # Detect listeners
        listener = self.detect_listener(message)

        # Detect and convert CLPv3 custom responses to CLPv4
        if (message["cmd"] == "direct") and ("val" in message):
            if self.validate({"cmd": str, "val": self.supporter.keydefaults["val"]},
                             message["val"]) == self.supporter.valid:
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
        if hasattr(self.cl_methods, message["cmd"]) and (message["cmd"] in self.safe_methods):
            method = getattr(self.cl_methods, message["cmd"])

        elif hasattr(self.custom_methods, message["cmd"]) and (message["cmd"] in self.safe_methods):
            method = getattr(self.custom_methods, message["cmd"])

        if method:
            # Run the method
            method(message, listener)
            self.__fire_event__(self.events.on_msg)

    def __session_on_message__(self, ws, message):
        try:
            message = json.loads(message)
            self.__method_handler__(message)
        except:
            pass

    def __session_on_connect__(self, ws):
        self.send_packet(cmd="handshake", listener=self.handshake_listener)

    def __session_on_error__(self, ws, error):
        self.log(f"Connection handler encountered an error: {error}")
        self.__fire_event__(self.events.on_error)

    def __session_on_close__(self, ws, close_status_code, close_msg):
        self.__fire_event__(self.events.on_close)

# Class for binding events
class events:
    def __init__(self):
        pass

    def on_connect(self):
        pass

    def on_msg(self):
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

    def gmsg(self, message, listener):
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
        self.parent.__fire_method_callbacks__(self.gmsg, message, listener)
        if listener:
            self.parent.__fire_method_listeners__(listener)

    def pmsg(self, message, listener):
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
        self.parent.__fire_method_callbacks__(self.pmsg, message, listener)
        if listener:
            self.parent.__fire_method_listeners__(listener)

    def gvar(self, message, listener):
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
        self.parent.__fire_method_callbacks__(self.gvar, message, listener)
        if listener:
            self.parent.__fire_method_listeners__(listener)

    def pvar(self, message, listener):
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
        self.parent.__fire_method_callbacks__(self.pvar, message, listener)
        if listener:
            self.parent.__fire_method_listeners__(listener)

    def direct(self, message, listener):
        # Fire callbacks for method and it's listener
        self.parent.__fire_method_callbacks__(self.direct, message, listener)
        if listener:
            self.parent.__fire_method_listeners__(listener)

    def ulist(self, message, listener):
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
        self.parent.__fire_method_callbacks__(self.ulist, message, listener)

    def server_version(self, message, listener):
        self.parent.server_version = message['val']

        # server_version will never return a listener
        self.parent.__fire_method_callbacks__(self.server_version, message, listener)

    def motd(self, message, listener):
        self.parent.motd_message = message['val']

        # motd will never return a listener
        self.parent.__fire_method_callbacks__(self.motd, message, listener)

    def client_ip(self, message, listener):
        self.parent.client_ip = message['val']

        # client_ip will never return a listener
        self.parent.__fire_method_callbacks__(self.client_ip, message, listener)

    def statuscode(self, message, listener):
        if listener:
            if listener in [self.parent.handshake_listener, self.parent.setid_listener]:
                human_ok, machine_ok = self.supporter.generate_statuscode("OK")
                match listener:
                    case self.parent.handshake_listener:
                        if (message["code"] == human_ok) or (message["code_id"] == machine_ok):
                            self.parent.__fire_event__(self.parent.events.on_connect)
                        else:
                            self.parent.shutdown()
                    case self.parent.setid_listener:
                        if (message["code"] == human_ok) or (message["code_id"] == machine_ok):
                            self.parent.username_set = True
                            self.parent.client_id = message["val"]
                            self.parent.__fire_event__(self.parent.events.on_username_set)
                    case self.parent.ping_listener:
                        self.parent.__fire_event__(self.parent.events.on_pong)
            else:
                self.parent.__fire_method_callbacks__(self.statuscode, message, listener)
                self.parent.__fire_method_listeners__(listener)
        else:
            self.parent.__fire_method_callbacks__(self.statuscode, message, listener)


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

    def exists(self, room_id: str):
        return hasattr(self, str(room_id))

    def create(self, room_id: str):
        if not self.exists(str(room_id)):
            setattr(self, str(room_id), self.__room__())

    def delete(self, room_id: str):
        if self.exists(str(room_id)):
            delattr(self, str(room_id))

    def get(self, room_id: str):
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
