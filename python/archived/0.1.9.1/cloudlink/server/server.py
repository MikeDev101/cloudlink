from .protocols import cl_methods, scratch_methods

import websockets
import asyncio
import json
from copy import copy


class server:
    def __init__(self, parent, logs: bool = True):
        self.version = parent.version

        # Initialize required libraries
        self.asyncio = asyncio
        self.websockets = websockets
        self.copy = copy
        self.json = json

        # Other
        self.enable_logs = logs
        self.id_counter = 0
        self.ip_blocklist = []

        # Config
        self.reject_clients = False
        self.enable_scratch_support = True
        self.check_ip_addresses = False
        self.enable_motd = False
        self.motd_message = str()

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

        # Initialize attributes from supporter component - This will also become part of the server's public API
        self.log = self.supporter.log
        self.validate = self.supporter.validate
        self.load_custom_methods = self.supporter.load_custom_methods
        self.disable_methods = self.supporter.disable_methods
        self.is_json = self.supporter.is_json
        self.get_client_ip = self.supporter.get_client_ip
        self.detect_listener = self.supporter.detect_listener
        self.generate_statuscode = self.supporter.generate_statuscode

        # Client and room management
        self.rooms = rooms(self)
        self.clients = clients(self)

        # Load Cloudlink methods
        self.cl_methods = cl_methods(self)

        # Load safe CLPv4 methods to mitigate vulnerabilities
        self.supporter.init_builtin_cl_methods()

        # Load Scratch cloud variable methods
        self.scratch_methods = scratch_methods(self)

    # == Public API functionality ==

    # Runs the server.
    def run(self, ip: str = "localhost", port: int = 3000):
        try:
            self.asyncio.run(self.__run__(ip, port))
        except KeyboardInterrupt:
            pass

    # Set the server's Message-of-the-Day.
    def set_motd(self, message: str, enable: bool = True):
        self.enable_motd = enable
        self.motd_message = message

    # Sets the client's username and enables private messages/variables, room link/unlink and direct functionality.
    def set_client_username(self, client: type, username: str):
        result = self.clients.set_username(client, username)
        if result:
            self.rooms.refresh(client, "default")

    # Links clients to rooms. Supports strings and lists/sets.
    def link_to_rooms(self, client: type, rooms_to_link=[]):
        # Prepare rooms
        rooms = set()
        if type(rooms_to_link) == str:
            rooms_to_link = [rooms_to_link]
        rooms.update(set(rooms_to_link))

        # Client cannot be linked to no rooms
        if len(rooms) == 0:
            rooms.update(["default"])

        # Manage existing rooms
        old_rooms = self.copy(client.rooms)
        if ("default" in client.rooms) and ("default" not in rooms):
            self.parent.rooms.unlink(client, "default")
        for room in old_rooms:
            self.parent.rooms.unlink(client, room)

        # Create rooms if they do not exist
        for room in rooms:
            if not self.parent.rooms.exists(room):
                self.parent.rooms.create(room)

        # Link client to new rooms
        for room in rooms:
            self.parent.rooms.link(client, room)
        new_rooms = self.copy(client.rooms)

    # Unlinks clients from rooms. Supports strings and lists/sets.
    def unlink_from_rooms(self, client: type, rooms_to_unlink=None):
        # Prepare the rooms
        rooms = set()
        if (not rooms_to_unlink) or (rooms_to_unlink and (len(rooms_to_unlink) == 0)):
            # Unlink all rooms
            rooms.update(self.copy(client.rooms))
        else:
            # Unlink from a single room, or many rooms
            if type(rooms_to_unlink) == list:
                rooms.update(set(rooms_to_unlink))
            else:
                rooms.update(rooms_to_unlink)

        # Unlink client from rooms
        old_rooms = self.copy(client.rooms)
        for room in rooms:
            self.parent.rooms.unlink(client, room)
        if len(client.rooms) == 0:
            # Reset to default room
            self.parent.rooms.link(client, "default")
        new_rooms = self.copy(client.rooms)

    # Binding callbacks - Provides a programmer-friendly interface to run extra code after a cloudlink method has been executed.
    def bind_callback(self, callback_method: type, function: type):
        if hasattr(self.cl_methods, callback_method.__name__) or hasattr(self.custom_methods, callback_method.__name__):
            if callback_method.__name__ not in self.method_callbacks:
                self.method_callbacks[callback_method.__name__] = set()
            self.method_callbacks[callback_method.__name__].add(function)

    # Binding events - Provides a programmer-friendly interface to detect client connects, disconnects, and errors.
    def bind_event(self, event_method: type, function: type):
        if hasattr(self.events, event_method.__name__):
            if event_method.__name__ not in self.event_callbacks:
                self.event_callbacks[event_method.__name__] = set()
            self.event_callbacks[event_method.__name__].add(function)

    # Multicasting variables - Automatically translates Scratch and Cloudlink. Used only for gvar.
    async def send_packet_multicast_variable(self, cmd: str, name: str, val: any = None, clients: type = None,
                                             exclude_client: any = None, room_id: str = None, new_name: str = None):
        # Get all clients present
        tmp_clients = None
        if clients:
            tmp_clients = set(clients)
        else:
            tmp_clients = set(self.copy(self.rooms.get(room_id).users))
            if not tmp_clients:
                return

        if exclude_client:
            tmp_clients.discard(exclude_client)
        clients_cl = set()
        clients_scratch = set()

        # Filter clients by protocol type
        for client in tmp_clients:
            match client.protocol:
                case self.supporter.proto_cloudlink:
                    clients_cl.add(client)
                case self.supporter.proto_scratch_cloud:
                    clients_scratch.add(client)

        # Methods that are marked with NoneType will not be translated
        translate_cl = {
            "set": "gvar",
            "create": "gvar",
            "delete": None,
            "rename": None
        }
        translate_scratch = {
            "gvar": "set",
            "pvar": None
        }

        # Translate between Scratch and Cloudlink
        if cmd in translate_cl:
            # Send message to all scratch protocol clients
            message = {"method": cmd, "name": name}
            tmp = self.copy(message)

            if val:
                message["value"] = val

                # Prevent crashing Scratch clients if the val is a dict / JSON object
                tmp = self.copy(message)
                if type(tmp["value"]) == dict:
                    tmp["value"] = self.json.dumps(tmp["value"])

            if new_name:
                message["new_name"] = new_name

            self.websockets.broadcast(clients_scratch, self.json.dumps(tmp))

            if (translate_cl[cmd]) and (len(clients_cl) != 0):
                # Send packet to only cloudlink protocol clients
                message = {"cmd": translate_cl[cmd], "name": name, "rooms": room_id}
                if val:
                    message["val"] = val

                    # Translate JSON string to dict
                    if type(message["val"]) == str:
                        try:
                            message["val"] = self.json.loads(message["val"])
                        except:
                            pass

                self.websockets.broadcast(clients_cl, self.json.dumps(message))

        elif cmd in translate_scratch:
            # Send packet to only cloudlink protocol clients
            message = {"cmd": cmd, "name": name, "val": val, "rooms": room_id}

            # Translate JSON string to dict
            if type(message["val"]) == str:
                try:
                    message["val"] = self.json.loads(message["val"])
                except:
                    pass

            self.websockets.broadcast(clients_cl, self.json.dumps(message))

            if (translate_scratch[cmd]) and (len(clients_scratch) != 0):
                # Send message to all scratch protocol clients
                message = {"method": translate_scratch[cmd], "name": name, "value": val}

                # Prevent crashing Scratch clients if the val is a dict / JSON object
                if type(message["value"]) == dict:
                    message["value"] = self.json.dumps(message["value"])

                self.websockets.broadcast(clients_scratch, self.json.dumps(message))
        else:
            raise TypeError("Command is not translatable!")

    # Multicast data - Used for gmsg, gvar, or multicasted direct messages.
    async def send_packet_multicast(self, cmd: str, val: any, clients: type = None, exclude_client: any = None,
                                    room_id: str = None, quirk: str = "quirk_embed_val"):
        # Get all clients present
        tmp_clients = None
        if clients:
            tmp_clients = set(clients)
        else:
            tmp_clients = set(self.copy(self.rooms.get(room_id).users))
            if not tmp_clients:
                return

        # Remove individual client
        if exclude_client:
            tmp_clients.discard(exclude_client)

        # Purge clients that aren't cloudlink
        for client in self.copy(tmp_clients):
            if client.protocol == self.supporter.proto_scratch_cloud:
                tmp_clients.discard(client)

        # Send packet to only cloudlink protocol clients
        message = {"cmd": cmd}
        if quirk == self.supporter.quirk_update_msg:
            message.update(val)
        elif quirk == self.supporter.quirk_embed_val:
            message["val"] = val
        else:
            raise ValueError("Unknown message quirk!")

        # Attach the rooms key
        if room_id:
            message["rooms"] = room_id

        # Send payload
        self.websockets.broadcast(tmp_clients, self.json.dumps(message))

    # Unicast data - Used for pmsg, pvar, or unicasted direct messages.
    async def send_packet_unicast(self, client: type, cmd: str, val: any, listener: str = None, room_id: str = None,
                                  quirk: str = "quirk_embed_val"):
        # Check client protocol
        if client.protocol == self.supporter.proto_unset:
            raise Exception("Cannot send packet to a client with an unset protocol!")
        if client.protocol != self.supporter.proto_cloudlink:
            raise TypeError("Unsupported protocol type!")

        # Manage specific message quirks
        message = {"cmd": cmd}
        if quirk == self.supporter.quirk_update_msg:
            message.update(val)
        elif quirk == self.supporter.quirk_embed_val:
            message["val"] = val
        else:
            raise TypeError("Unknown message quirk!")

        # Attach a listener response
        if listener:
            message["listener"] = listener

        # Attach the rooms key
        if room_id:
            message["rooms"] = room_id

        # Send payload
        try:
            await client.send(self.json.dumps(message))
        except self.websockets.exceptions.ConnectionClosedError:
            self.log(f"Failed to send packet to client {client.id}: Connection closed unexpectedly")

    # Unicast status codes - Only used for statuscode.
    async def send_code(self, client: type, code: str, extra_data: dict = None, listener: str = None):
        # Check client protocol
        if client.protocol == self.supporter.proto_unset:
            raise Exception("Cannot send codes to a client with an unset protocol!")
        if client.protocol != self.supporter.proto_cloudlink:
            raise TypeError("Unsupported protocol type!")

        # Prepare message
        human_code, machine_code = self.generate_statuscode(code)
        message = {
            "cmd": "statuscode",
            "code": human_code,
            "code_id": machine_code
        }

        # Attach extra data
        if extra_data:
            message.update(extra_data)

        # Attach a listener response
        if listener:
            message["listener"] = listener

        # Send payload
        try:
            await client.send(self.json.dumps(message))
        except self.websockets.exceptions.ConnectionClosedError:
            self.log(f"Failed to send status code to client {client.id}: Connection closed unexpectedly")

    # == Server functionality ==

    async def __run__(self, ip, port):
        # Main event loop
        async with self.websockets.serve(self.__handler__, ip, port):
            await self.asyncio.Future()

    def __fire_callbacks__(self, callback_method, client, message, listener):
        if callback_method.__name__ in self.method_callbacks:
            for _method in self.method_callbacks[callback_method.__name__]:
                self.asyncio.create_task(_method(client, message, listener))

    def __fire_event__(self, event_method, client):
        if event_method.__name__ in self.event_callbacks:
            for _method in self.event_callbacks[event_method.__name__]:
                self.asyncio.create_task(_method(client))

    async def __cl_method_handler__(self, client: type, message: dict):
        # Check if the message contains the cmd key, with a string datatype.
        match self.validate({"cmd": str}, message):
            case self.supporter.invalid:
                return self.supporter.invalid
            case self.supporter.missing_key:
                return self.supporter.missing_key
            case self.supporter.not_a_dict:
                raise TypeError

        # Detect and convert CLPv3 custom requests to CLPv4
        if (message["cmd"] == "direct") and ("val" in message):
            if self.validate({"cmd": str, "val": self.supporter.keydefaults["val"]},
                             message["val"]) == self.supporter.valid:
                tmp_msg = {
                    "cmd": message["val"]["cmd"],
                    "val": message["val"]["val"]
                }
                message = self.copy(tmp_msg)

        # Detect listeners
        listener = self.detect_listener(message)

        # Check if the command is disabled
        if message["cmd"] in self.disabled_methods:
            return self.supporter.disabled_method

        # Check if the command method exists
        # Custom methods override / take precedence over builtin methods
        if hasattr(self.custom_methods, message["cmd"]) and (message["cmd"] in self.safe_methods):
            method = getattr(self.custom_methods, message["cmd"])

            await method(client, message, listener)
            self.__fire_callbacks__(method, client, message, listener)

            return self.supporter.valid

        # Run builtin method
        elif hasattr(self.cl_methods, message["cmd"]) and (message["cmd"] in self.safe_methods):
            method = getattr(self.cl_methods, message["cmd"])

            await method(client, message, listener)
            self.__fire_callbacks__(method, client, message, listener)

            return self.supporter.valid

        # Method not found
        else:
            return self.supporter.unknown_method

    async def __scratch_method_handler__(self, client: type, message: dict):
        # Check if the message contains the method key, with a string datatype.
        match self.validate({"method": str}, message):
            case self.supporter.invalid:
                return self.supporter.invalid
            case self.supporter.missing_key:
                return self.supporter.missing_key
            case self.supporter.not_a_dict:
                raise TypeError

        # Check if the command method exists
        if not hasattr(self.scratch_methods, message["method"]):
            return self.supporter.unknown_method

        # Run the method
        await getattr(self.scratch_methods, message["method"])(client, message)
        return self.supporter.valid

    async def __run_method__(self, client: type, message: dict):
        # Detect connection protocol (supports Cloudlink CLPv4 or Scratch Cloud Variables Protocol)
        if client.protocol == self.supporter.proto_unset:
            if "cmd" in message:
                # Update the client's protocol type and update the clients iterable
                client.protocol = self.supporter.proto_cloudlink
                self.clients.set_protocol(client, self.supporter.proto_cloudlink)

                # Link client to the default room
                self.rooms.link(client, "default")

                return await self.__cl_method_handler__(client, message)

            elif "method" in message:
                if not self.enable_scratch_support:
                    await client.close(code=1000, reason="Scratch protocol is disabled")
                    return

                # Update the client's protocol type and update the clients iterable
                client.protocol = self.supporter.proto_scratch_cloud
                self.clients.set_protocol(client, self.supporter.proto_scratch_cloud)

                return await self.__scratch_method_handler__(client, message)
            else:
                # Reject the client because the server does not understand the protocol being used
                return self.supporter.unknown_protocol

        elif client.protocol == self.supporter.proto_cloudlink:
            # Interpret and process CL commands
            return await self.__cl_method_handler__(client, message)

        elif client.protocol == self.supporter.proto_scratch_cloud:
            # Interpret and process Scratch commands
            return await self.__scratch_method_handler__(client, message)

        else:
            raise TypeError(f"Unknown protocol type: {client.protocol}")

    async def __handler__(self, client):
        if self.check_ip_addresses:
            # Get the IP address of client
            client.full_ip = self.get_client_ip(client)

        rejected = False
        if self.reject_clients:
            rejected = True
            await client.close(code=1013, reason="Reject mode is enabled")
        elif self.check_ip_addresses and (client.full_ip in self.ip_blocklist):
            rejected = True
            await client.close(code=1008, reason="IP blocked")

        # Do absolutely nothing if the client was rejected
        if not rejected:
            # Set the initial protocol type
            client.protocol = self.supporter.proto_unset

            # Assign an ID to the client
            client.id = self.id_counter
            self.id_counter += 1

            # Register the client
            self.clients.create(client)

            # Configure client
            client.rooms = set()
            client.username_set = False
            client.linked = False
            client.friendly_username = None

            # Fire events
            self.__fire_event__(self.events.on_connect, client)

            # Handle requests from the client
            try:
                async for tmp_msg in client:
                    # Handle empty payloads
                    if len(tmp_msg) == 0:
                        if client.protocol == self.supporter.proto_cloudlink:
                            await self.send_code(client, "EmptyPacket")
                            continue
                        elif client.protocol == self.supporter.proto_scratch_cloud:
                            await client.close(code=self.supporter.connection_error, reason="Empty message")
                        else:
                            await client.close(code=1002, reason="Empty message")

                    # Convert/sanity check JSON
                    message = None
                    try:
                        message = self.json.loads(tmp_msg)
                    except:
                        if client.protocol == self.supporter.proto_cloudlink:
                            await self.send_code(client, "Syntax")
                            continue
                        elif client.protocol == self.supporter.proto_scratch_cloud:
                            await client.close(code=self.supporter.connection_error, reason="Corrupt/malformed JSON")
                        else:
                            await client.close(code=1002, reason="Corrupt/malformed JSON")

                        # Fire events
                        self.__fire_event__(self.events.on_error, client)

                    # Run handlers
                    if message:
                        # Convert keys in the packet to proper JSON (Primarily for Scratch-based clients)
                        for key in message.keys():
                            if type(message[key]) == str:
                                if self.supporter.is_json(message[key]):
                                    message[key] = self.json.loads(message[key])

                        result = await self.__run_method__(client, message)
                        match result:
                            case self.supporter.disabled_method:
                                listener = self.supporter.detect_listener(message)
                                await self.send_code(client, "Disabled", listener=listener)

                            case self.supporter.invalid:
                                if client.protocol == self.supporter.proto_cloudlink:
                                    listener = self.supporter.detect_listener(message)
                                    await self.send_code(client, "Syntax", listener=listener)

                                elif client.protocol == self.proto_scratch_cloud:
                                    await client.close(code=self.supporter.connection_error, reason="Bad method")

                            case self.supporter.missing_key:
                                if client.protocol == self.supporter.proto_cloudlink:
                                    listener = self.supporter.detect_listener(message)
                                    await self.send_code(client, "Syntax", listener=listener)

                                elif client.protocol == self.proto_scratch_cloud:
                                    await client.close(code=self.supporter.connection_error,
                                                       reason="Missing method key in JSON")

                            case self.supporter.unknown_method:
                                if client.protocol == self.supporter.proto_cloudlink:
                                    listener = self.supporter.detect_listener(message)
                                    await self.send_code(client, "Invalid", listener=listener)

                                elif client.protocol == self.proto_scratch_cloud:
                                    await client.close(code=self.supporter.connection_error, reason="Invalid method")

                            case self.supporter.unknown_protocol:
                                await client.close(code=1002, reason="Unknown protocol")

            # Handle unexpected disconnects
            except self.websockets.exceptions.ConnectionClosedError:
                pass

            # Handle OK disconnects
            except self.websockets.exceptions.ConnectionClosedOK:
                pass

            # Handle unexpected exceptions
            except Exception as e:
                self.log(f"Exception was raised: \"{e}\"\n{self.supporter.full_stack()}")
                await client.close(code=1011, reason="Unexpected exception was raised")

            # Gracefully shutdown the handler
            finally:
                if client.username_set and (client.protocol == self.supporter.proto_cloudlink):
                    # Alert clients that a client has disconnected
                    rooms = self.copy(client.rooms)
                    for room in rooms:
                        self.rooms.unlink(client, room)
                        room_data = self.rooms.get(room)
                        if not room_data:
                            continue

                        # Update the state
                        await self.send_packet_multicast(
                            cmd="ulist",
                            val={
                                "mode": "remove",
                                "val": self.clients.convert_json(client)
                            },
                            quirk=self.supporter.quirk_update_msg,
                            room_id=room
                        )

                # Dispose the client
                self.clients.delete(client)

                # Fire events
                self.__fire_event__(self.events.on_close, client)


# Class to store custom methods
class custom_methods:
    def __init__(self):
        pass


# Clients management
class clients:
    def __init__(self, parent):
        self.__all_cl__ = set()
        self.__all_scratch__ = set()
        self.__proto_unset__ = parent.supporter.proto_unset
        self.__proto_cloudlink__ = parent.supporter.proto_cloudlink
        self.__proto_scratch_cloud__ = parent.supporter.proto_scratch_cloud
        self.__parent__ = parent
        self.__usernames__ = dict()

    def get_all_scratch(self):
        return self.__all_scratch__

    def get_all_cloudlink(self):
        return self.__all_cl__

    def get_all_usernames(self):
        return self.__usernames__

    def get_all(self):
        tmp = self.__parent__.copy(self.__dict__)

        # Remove attributes that aren't client objects
        del tmp["__all_cl__"]
        del tmp["__all_scratch__"]
        del tmp["__proto_unset__"]
        del tmp["__proto_cloudlink__"]
        del tmp["__proto_scratch_cloud__"]
        del tmp["__usernames__"]
        del tmp["__parent__"]

        return tmp

    def set_protocol(self, client: dict, protocol: str):
        match protocol:
            case self.__proto_cloudlink__:
                self.__all_cl__.add(client)
            case self.__proto_scratch_cloud__:
                self.__all_scratch__.add(client)
            case _:
                raise TypeError(f"Unsupported protocol ID: {protocol}")

        if self.exists(client):
            self.get(client).protocol = protocol

        else:
            raise ValueError

    def exists(self, client: dict):
        return hasattr(self, str(client.id))

    def create(self, client: dict):
        if not self.exists(client):
            setattr(self, str(client.id), client)

    def set_username(self, client: dict, username: str):
        # Abort if the client is invalid
        if not self.exists(client):
            return self.__parent__.supporter.username_not_set

        # Create new username set if not present
        if not str(username) in self.__usernames__:
            self.__usernames__[str(username)] = set()

        # Add pointer to client object
        self.__usernames__[str(username)].add(client)

        # Client username has been set successfully
        client.friendly_username = str(username)
        client.username_set = True
        return self.__parent__.supporter.username_set

    def delete(self, client: dict):
        if self.exists(client):
            # Remove user from client type lists
            match self.get(client).protocol:
                case self.__proto_cloudlink__:
                    self.__all_cl__.remove(client)
                case self.__proto_scratch_cloud__:
                    self.__all_scratch__.remove(client)
                case self.__proto_unset__:
                    pass
                case _:
                    raise TypeError(f"Unsupported protocol ID: {self.get(client).protocol}")

            # Remove the username from the userlist
            if client.username_set:
                if str(client.friendly_username) in self.__usernames__:
                    # Remove client from the shared username set
                    if client in self.__usernames__[str(client.friendly_username)]:
                        self.__usernames__[str(client.friendly_username)].remove(client)

                    # Delete the username if there are no more users present with that name
                    if len(self.__usernames__[str(client.friendly_username)]) == 0:
                        del self.__usernames__[str(client.friendly_username)]

            # Clean up rooms
            if hasattr(client, "rooms") and client.rooms:
                for room in self.__parent__.copy(client.rooms):
                    self.__parent__.rooms.unlink(client, room)

            # Dispose the client
            delattr(self, str(client.id))

    def get(self, client: dict):
        if self.exists(client):
            return getattr(self, str(client.id))
        else:
            return None

    def convert_json(self, client: any):
        return {"username": client.friendly_username, "id": client.id}

    def find_multi_obj(self, clients_to_find, rooms="default"):
        if not type(rooms) in [set, list]:
            rooms = {rooms}

        tmp = set()

        # Check if the input is iterable
        if type(clients_to_find) in [list, set]:
            for room in rooms:
                for client in clients_to_find:
                    res = self.find_obj(client, room)
                    if not res:
                        continue
                    if type(res) in [list, set]:
                        tmp.update(res)
                    else:
                        tmp.add(res)
        else:
            for room in rooms:
                res = self.find_obj(clients_to_find, room)
                if not res:
                    continue
                if type(res) in [list, set]:
                    tmp.update(res)
                else:
                    tmp.add(res)

        return tmp

    def find_obj(self, client_to_find, room_id=None):
        room_user_objs = set()
        room_user_names = dict()
        if room_id:
            if not self.__parent__.rooms.exists(room_id):
                return None

            room_user_objs = self.__parent__.rooms.get(room_id).clients
            room_user_names = self.__parent__.rooms.get(room_id).usernames_searchable
        else:
            room_user_objs = self.get_all()
            room_user_names = self.get_all_usernames()

        if type(client_to_find) == str:
            if client_to_find in room_user_names:
                return room_user_names[client_to_find]

        elif type(client_to_find) == dict:
            if "id" in client_to_find:
                if str(client_to_find["id"]) in room_user_objs:
                    return room_user_objs[str(client_to_find["id"])]

        elif type(client_to_find) == int:
            if str(client_to_find) in room_user_objs:
                return room_user_objs[str(client_to_find)]

        else:
            return None


# Rooms management
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

    def unlink(self, client, room_id):
        room_data = self.get(room_id)
        if room_data:
            # Remove the user from the room
            if client in room_data.users:
                room_data.users.remove(client)

            if client.username_set:
                # Remove the user from the room's JSON-friendly userlist
                user_json = self.__parent__.clients.convert_json(client)
                if user_json in room_data.userlist:
                    room_data.userlist.remove(user_json)

                if client.friendly_username in room_data.usernames:
                    room_data.usernames.remove(client.friendly_username)

                if (not room_id == "default") and (len(room_data.users) == 0):
                    self.delete(room_id)

                if str(client.id) in room_data.clients:
                    del room_data.clients[str(client.id)]

                if client.friendly_username in room_data.usernames_searchable:
                    del room_data.usernames_searchable[client.friendly_username]

        if room_id in client.rooms:
            client.rooms.remove(room_id)

    def link(self, client, room_id):
        # Get the room data
        room_data = self.get(room_id)
        if room_data:
            # Add the user to the room
            room_data.users.add(client)

            if room_id not in client.rooms:
                client.rooms.add(room_id)

            if client.username_set:
                # Add the user to the room's JSON-friendly userlist
                user_json = self.__parent__.clients.convert_json(client)
                room_data.userlist.append(user_json)

                if client.friendly_username not in room_data.usernames:
                    room_data.usernames.add(client.friendly_username)

                if str(client.id) not in room_data.clients:
                    room_data.clients[str(client.id)] = client

                if client.friendly_username not in room_data.usernames_searchable:
                    room_data.usernames_searchable[client.friendly_username] = set()

                if client not in room_data.usernames_searchable[client.friendly_username]:
                    room_data.usernames_searchable[client.friendly_username].add(client)

    def refresh(self, client, room_id):
        if self.exists(room_id):
            self.unlink(client, room_id)
            self.link(client, room_id)

    class __room__:
        def __init__(self):
            # Global data stream current value
            self.global_data_value = str()

            # Storage of all global variables / Scratch Cloud Variables
            self.global_vars = dict()

            # User management
            self.users = set()
            self.usernames = set()
            self.userlist = list()

            # Client management
            self.clients = dict()

            # Used only for string-based user lookup
            self.usernames_searchable = dict()


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
