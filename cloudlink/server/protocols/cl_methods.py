class cl_methods:
    def __init__(self, parent):
        self.parent = parent
        self.supporter = parent.supporter
        self.copy = parent.copy
        self.rooms = parent.rooms
        self.get_rooms = parent.supporter.get_rooms
        self.clients = parent.clients

        # Various ways to send messages
        self.send_packet_unicast = parent.send_packet_unicast
        self.send_packet_multicast = parent.send_packet_multicast
        self.send_packet_multicast_variable = parent.send_packet_multicast_variable
        self.send_code = parent.send_code

        # Get protocol types to allow cross-protocol data sync
        self.proto_scratch_cloud = self.supporter.proto_scratch_cloud
        self.proto_cloudlink = self.supporter.proto_cloudlink

        # Packet check definitions - Specifies required keys, their datatypes, and optional keys
        self.validator = {
            self.gmsg: {
                "required": {
                    "val": self.supporter.keydefaults["val"],
                    "listener": self.supporter.keydefaults["listener"],
                    "rooms": self.supporter.keydefaults["rooms"]
                },
                "optional": ["listener", "rooms"],
                "sizes": {
                    "val": 1000
                }
            },
            self.pmsg: {
                "required": {
                    "val": self.supporter.keydefaults["val"],
                    "id": self.supporter.keydefaults["id"],
                    "listener": self.supporter.keydefaults["listener"],
                    "rooms": self.supporter.keydefaults["rooms"]
                },
                "optional": ["listener", "rooms"],
                "sizes": {
                    "val": 1000
                }
            },
            self.gvar: {
                "required": {
                    "val": self.supporter.keydefaults["val"],
                    "name": self.supporter.keydefaults["name"],
                    "listener": self.supporter.keydefaults["listener"],
                    "rooms": self.supporter.keydefaults["rooms"]
                },
                "optional": ["listener", "rooms"],
                "sizes": {
                    "val": 1000
                }
            },
            self.pvar: {
                "required": {
                    "val": self.supporter.keydefaults["val"],
                    "name": self.supporter.keydefaults["name"],
                    "id": self.supporter.keydefaults["id"],
                    "listener": self.supporter.keydefaults["listener"],
                    "rooms": self.supporter.keydefaults["rooms"]
                },
                "optional": ["listener", "rooms"],
                "sizes": {
                    "val": 1000
                }
            },
            self.setid: {
                "required": {
                    "val": self.supporter.keydefaults["val"],
                    "listener": self.supporter.keydefaults["listener"],
                    "rooms": self.supporter.keydefaults["rooms"]
                },
                "optional": ["listener", "rooms"],
                "sizes": {
                    "val": 1000
                }
            },
            self.link: {
                "required": {
                    "val": self.supporter.keydefaults["rooms"],
                    "listener": self.supporter.keydefaults["listener"]
                },
                "optional": ["listener"],
                "sizes": {
                    "val": 1000
                }
            },
            self.unlink: {
                "required": {
                    "val": self.supporter.keydefaults["rooms"],
                    "listener": self.supporter.keydefaults["listener"]
                },
                "optional": ["val", "listener"],
                "sizes": {
                    "val": 1000
                }
            },
            self.direct: {
                "required": {
                    "val": self.supporter.keydefaults["val"],
                    "id": self.supporter.keydefaults["id"],
                    "listener": self.supporter.keydefaults["listener"],
                    "rooms": self.supporter.keydefaults["rooms"]
                },
                "optional": ["id", "listener", "rooms"],
                "sizes": {
                    "val": 1000
                }
            }
        }

    async def __auto_validate__(self, validator, client, message, listener):
        validation = self.supporter.validate(
            keys=validator["required"],
            payload=message,
            optional=validator["optional"],
            sizes=validator["sizes"]
        )

        match validation:
            case self.supporter.invalid:
                # Command datatype is invalid
                await self.parent.send_code(client, "DataType", listener=listener)
                return False
            case self.supporter.missing_key:
                # Command syntax is invalid
                await self.parent.send_code(client, "Syntax", listener=listener)
                return False
            case self.supporter.too_large:
                # Payload size overload
                await self.parent.send_code(client, "TooLarge", listener=listener)
                return False

        return True

    async def handshake(self, client, message, listener):
        # Validation is not needed since this command takes no arguments

        if self.parent.check_ip_addresses:
            # Report client's IP
            await self.send_packet_unicast(
                client=client,
                cmd="client_ip",
                val=client.full_ip,
                quirk=self.supporter.quirk_embed_val
            )

        # Report server version
        await self.send_packet_unicast(
            client=client,
            cmd="server_version",
            val=self.parent.version,
            quirk=self.supporter.quirk_embed_val
        )

        # Report server MOTD
        if self.parent.enable_motd:
            await self.send_packet_unicast(
                client=client,
                cmd="motd",
                val=self.parent.motd_message,
                quirk=self.supporter.quirk_embed_val
            )

        # Report the current userlist
        room_data = self.parent.rooms.get("default")
        await self.send_packet_unicast(
            client=client,
            cmd="ulist",
            val={
                "mode": "set",
                "val": room_data.userlist
            },
            room_id="default",
            quirk=self.supporter.quirk_update_msg
        )

        # Report the cached gmsg value
        await self.send_packet_unicast(
            client=client,
            cmd="gmsg",
            val=room_data.global_data_value,
            room_id="default",
            quirk=self.supporter.quirk_embed_val
        )

        # Tell the client that the cloudlink protocol was selected
        await self.send_code(
            client=client,
            code="OK",
            listener=listener
        )

    async def ping(self, client, message, listener):
        # Validation is not needed since this command takes no arguments

        # Return ping
        await self.send_code(
            client=client,
            code="OK",
            listener=listener
        )

    async def gmsg(self, client, message, listener):
        # Validate the message syntax and datatypes
        if not await self.__auto_validate__(self.validator[self.gmsg], client, message, listener):
            return

        # Get rooms
        rooms = self.get_rooms(client, message)

        # Send to all rooms specified
        exclude_client = None
        if listener:
            exclude_client = client

        # Cache the room's gmsg value
        for room in self.copy(rooms):
            self.rooms.get(room).global_data_value = message["val"]

        # Send to all rooms specified
        for room in rooms:
            await self.send_packet_multicast(
                cmd="gmsg",
                val=message["val"],
                room_id=room,
                exclude_client=exclude_client,
                quirk=self.supporter.quirk_embed_val,
            )

            # Handle listeners
            if listener:
                await self.send_packet_unicast(
                    client=client,
                    cmd="gmsg",
                    val=message["val"],
                    room_id=room,
                    listener=listener
                )

    async def pmsg(self, client, message, listener):
        # Validate the message syntax and datatypes
        if not await self.__auto_validate__(self.validator[self.pmsg], client, message, listener):
            return

        # Check if the client has set their username
        if not client.username_set:
            await self.send_code(client, "IDRequired", listener=listener)
            return

        # Get rooms
        rooms = self.get_rooms(client, message)

        # Get the origin of the request
        origin = self.clients.convert_json(client)

        # Locate clients to send message to
        clients = set()
        for room in rooms:
            clients.update(self.clients.find_multi_obj(message["id"], room))

        # Can't send message since no clients were found
        if len(clients) == 0:
            await self.send_code(client, "IDNotFound", listener=listener)
            return

        # Send to all rooms specified
        for room in rooms:
            await self.send_packet_multicast(
                cmd="pmsg",
                val={
                    "val": message["val"],
                    "origin": origin,
                    "rooms": room
                },
                clients=clients,
                quirk=self.supporter.quirk_update_msg,
            )

        # Tell the client the message was sent OK
        await self.send_code(client, "OK", listener=listener)

    async def gvar(self, client, message, listener):
        # Validate the message syntax and datatypes
        if not await self.__auto_validate__(self.validator[self.gvar], client, message, listener):
            return

        # Get rooms
        rooms = self.get_rooms(client, message)

        # Send to all rooms specified
        exclude_client = None
        if listener:
            exclude_client = client

        # Cache the room's current gvar value
        for room in self.copy(rooms):
            room_data = self.rooms.get(room)
            if message["name"] in room_data.global_vars:
                room_data.global_vars[message["name"]] = message["val"]
            else:
                room_data.global_vars[message["name"]] = message["val"]

        # Send to all rooms specified (auto convert to scratch format)
        for room in rooms:
            room_data = self.parent.rooms.get(room)

            await self.send_packet_multicast_variable(
                cmd="gvar",
                name=message["name"],
                val=message["val"],
                room_id=room,
                exclude_client=exclude_client
            )

        # Handle listeners
        if listener and (len(rooms) != 0):
            await self.send_packet_unicast(
                client=client,
                cmd="gvar",
                val={
                    "name": message["name"],
                    "val": message["val"]
                },
                quirk=self.supporter.quirk_update_msg,
                listener=listener
            )

    async def pvar(self, client, message, listener):
        # Validate the message syntax and datatypes
        if not await self.__auto_validate__(self.validator[self.pvar], client, message, listener):
            return

        # Check if the client has set their username
        if not client.username_set:
            await self.send_code(client, "IDRequired", listener=listener)
            return

        # Get rooms
        rooms = self.get_rooms(client, message)

        # Get the origin of the request
        origin = self.clients.convert_json(client)

        # Locate clients to send message to
        clients = set()
        for room in rooms:
            clients.update(self.clients.find_multi_obj(message["id"], room))

        # Can't send message since no clients were found
        if len(clients) == 0:
            await self.send_code(client, "IDNotFound", listener=listener)
            return

        # Send to all rooms specified
        for room in rooms:
            await self.send_packet_multicast(
                cmd="pvar",
                val={
                    "val": message["val"],
                    "name": message["name"],
                    "origin": origin,
                    "rooms": room
                },
                clients=clients,
                quirk=self.supporter.quirk_update_msg,
            )

        # Tell the client the message was sent OK
        await self.send_code(client, "OK", listener=listener)

    async def setid(self, client, message, listener):
        # Validate the message syntax and datatypes
        if not await self.__auto_validate__(self.validator[self.setid], client, message, listener):
            return

        if client.username_set:
            await self.send_code(client, "IDSet", listener=listener)
            return

        result = self.parent.clients.set_username(client, message["val"])
        if result == self.supporter.username_set:
            await self.send_code(client, "OK", extra_data={"val": self.parent.clients.convert_json(client)},
                                 listener=listener)
        else:
            await self.send_code(client, "IDConflict", listener=listener)
            return

        # Refresh room
        self.parent.rooms.refresh(client, "default")

        # Update all userlists
        await self.send_packet_multicast(
            cmd="ulist",
            val={
                "mode": "add",
                "val": self.parent.clients.convert_json(client)
            },
            quirk=self.supporter.quirk_update_msg,
            room_id="default"
        )

    async def link(self, client, message, listener):
        # Validate the message syntax and datatypes
        if not await self.__auto_validate__(self.validator[self.link], client, message, listener):
            return

        if not client.username_set:
            await self.send_code(client, "IDRequired", listener=listener)
            return

        # Prepare rooms
        rooms = set()
        if type(message["val"]) == str:
            message["val"] = [message["val"]]
        rooms.update(set(message["val"]))

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

        # Tell the client they have been linked
        await self.send_code(client, "OK", listener=listener)

        # Update old userlist
        for room in old_rooms:
            # Prevent duplication
            if room in new_rooms:
                continue

            # Get the room data
            room_data = self.parent.rooms.get(room)
            if not room_data:
                continue

            # Update the state
            await self.send_packet_multicast(
                cmd="ulist",
                val={
                    "mode": "set",
                    "val": room_data.userlist
                },
                quirk=self.supporter.quirk_update_msg,
                room_id=room
            )

        # Update new userlist
        for room in new_rooms:
            # Get the room data
            room_data = self.parent.rooms.get(room)
            if not room_data:
                continue

            # Update the state
            await self.send_packet_multicast(
                cmd="ulist",
                val={
                    "mode": "set",
                    "val": room_data.userlist
                },
                quirk=self.supporter.quirk_update_msg,
                room_id=room
            )

        # Sync the global variable state
        for tmp_room in client.rooms:
            room_data = self.parent.rooms.get(tmp_room)
            if len(room_data.global_vars.keys()) != 0:
                # Update the client's state
                for var in room_data.global_vars.keys():
                    await self.send_packet_unicast(
                        client=client,
                        cmd="gvar",
                        val={
                            "name": var,
                            "val": room_data.global_vars[var]
                        },
                        quirk=self.supporter.quirk_update_msg,
                        room_id=tmp_room
                    )

            # Report the room's cached gmsg value
            await self.send_packet_unicast(
                client=client,
                cmd="gmsg",
                val=room_data.global_data_value,
                quirk=self.supporter.quirk_embed_val,
                room_id=tmp_room
            )

    async def unlink(self, client, message, listener):
        # Validate the message syntax and datatypes
        if not await self.__auto_validate__(self.validator[self.unlink], client, message, listener):
            return

        if not client.username_set:
            await self.send_code(client, "IDRequired", listener=listener)
            return

        # Prepare the rooms
        rooms = set()
        if ("val" not in message) or (("val" in message) and (len(message["val"]) == 0)):
            # Unlink all rooms
            rooms.update(self.copy(client.rooms))
        else:
            # Unlink from a single room, or many rooms
            if type(message["val"]) == list:
                rooms.update(set(message["val"]))
            else:
                rooms.update(message["val"])

        # Unlink client from rooms
        old_rooms = self.copy(client.rooms)
        for room in rooms:
            self.parent.rooms.unlink(client, room)
        if len(client.rooms) == 0:
            # Reset to default room
            self.parent.rooms.link(client, "default")
        new_rooms = self.copy(client.rooms)

        # Tell the client they have been unlinked
        await self.send_code(client, "OK", listener=listener)

        # Update old userlist
        for room in old_rooms:
            # Prevent duplication
            if room in new_rooms:
                continue

            # Get the room data
            room_data = self.parent.rooms.get(room)
            if not room_data:
                continue

            # Update the state
            await self.send_packet_multicast(
                cmd="ulist",
                val={
                    "mode": "set",
                    "val": room_data.userlist
                },
                quirk=self.supporter.quirk_update_msg,
                room_id=room
            )

        # Update new userlist
        for room in new_rooms:
            # Get the room data
            room_data = self.parent.rooms.get(room)
            if not room_data:
                continue

            # Update the state
            await self.send_packet_multicast(
                cmd="ulist",
                val={
                    "mode": "set",
                    "val": room_data.userlist
                },
                quirk=self.supporter.quirk_update_msg,
                room_id=room
            )

        # Sync the global variable state
        for tmp_room in client.rooms:
            room_data = self.parent.rooms.get(tmp_room)
            if len(room_data.global_vars.keys()) != 0:
                # Update the client's state
                for var in room_data.global_vars.keys():
                    await self.send_packet_unicast(
                        client=client,
                        cmd="gvar",
                        val={
                            "name": var,
                            "val": room_data.global_vars[var]
                        },
                        room_id=tmp_room,
                        quirk=self.supporter.quirk_update_msg
                    )

            # Report the room's cached gmsg value
            await self.send_packet_unicast(
                client=client,
                cmd="gmsg",
                val=room_data.global_data_value,
                quirk=self.supporter.quirk_embed_val,
                room_id=tmp_room
            )

    async def direct(self, client, message, listener):
        # Validate the message syntax and datatypes
        if not await self.__auto_validate__(self.validator[self.direct], client, message, listener):
            return

        # Legacy command formatting will be automatically converted to new format, so this function defaults to doing nothing unless an ID is specified
        if "id" in message:
            # Attempting to send a packet directly to someone/something
            if not client.username_set:
                await self.send_code(client, "IDRequired", listener=listener)
                return

            # Get the origin of the request
            origin = self.clients.convert_json(client)

            # Locate all clients to send the direct data to
            clients = self.clients.find_multi_obj(message["id"], None)

            if not clients:
                await self.send_code(client, "IDNotFound", listener=listener)
                return

            if (type(clients) in [list, set]) and (len(clients) == 0):
                await self.send_code(client, "IDNotFound", listener=listener)
                return

            await self.send_packet_multicast(
                cmd="direct",
                val={
                    "val": message["val"],
                    "origin": origin
                },
                clients=clients,
                quirk=self.supporter.quirk_update_msg
            )
