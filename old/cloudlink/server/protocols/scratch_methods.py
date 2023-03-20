class scratch_methods:
    def __init__(self, parent):
        self.parent = parent
        self.supporter = parent.supporter
        self.json = parent.json
        self.copy = parent.copy
        self.log = parent.supporter.log

        # Various ways to send messages
        self.send_packet_unicast = parent.send_packet_unicast
        self.send_packet_multicast = parent.send_packet_multicast
        self.send_packet_multicast_variable = parent.send_packet_multicast_variable

        # Get protocol types to allow cross-protocol data sync
        self.proto_scratch_cloud = self.supporter.proto_scratch_cloud
        self.proto_cloudlink = self.supporter.proto_cloudlink

        # Packet check definitions - Specifies required keys, their datatypes, and optional keys
        self.validator = {
            self.handshake: {
                "required": {
                    "method": self.supporter.keydefaults["method"],
                    "project_id": self.supporter.keydefaults["project_id"],
                    "user": self.supporter.keydefaults["user"]
                },
                "optional": [],
                "sizes": {
                    "project_id": 100,
                    "user": 20
                }
            },
            self.set: {
                "required": {
                    "method": self.supporter.keydefaults["method"],
                    "name": self.supporter.keydefaults["name"],
                    "value": self.supporter.keydefaults["value"]
                },
                "optional": [],
                "sizes": {
                    "name": 21,
                    "value": 1000
                }
            },
            self.create: {
                "required": {
                    "method": self.supporter.keydefaults["method"],
                    "name": self.supporter.keydefaults["name"],
                    "value": self.supporter.keydefaults["value"]
                },
                "optional": [],
                "sizes": {
                    "name": 21,
                    "value": 1000
                }
            },
            self.delete: {
                "required": {
                    "method": self.supporter.keydefaults["method"],
                    "name": self.supporter.keydefaults["name"]
                },
                "optional": [],
                "sizes": {
                    "name": 21
                }
            },
            self.rename: {
                "required": {
                    "method": self.supporter.keydefaults["method"],
                    "name": self.supporter.keydefaults["name"],
                    "new_name": self.supporter.keydefaults["name"]
                },
                "optional": [],
                "sizes": {
                    "name": 21,
                    "new_name": 21
                }
            }
        }

    async def __auto_validate__(self, validator, client, message):
        validation = self.supporter.validate(
            keys=validator["required"],
            payload=message,
            optional=validator["optional"],
            sizes=validator["sizes"]
        )

        match validation:
            case self.supporter.invalid:
                # Command datatype is invalid
                await client.close(code=self.supporter.connection_error, reason="Invalid datatype error")
                return False
            case self.supporter.missing_key:
                # Command syntax is invalid
                await client.close(code=self.supporter.connection_error, reason="Syntax error")
                return False
            case self.supporter.too_large:
                # Payload size overload
                await client.close(code=self.supporter.connection_error, reason="Contents too large")
                return False

        return True

    async def handshake(self, client, message):
        # Validate the message syntax and datatypes
        if not await self.__auto_validate__(self.validator[self.handshake], client, message):
            return

        # According to the Scratch cloud variable spec, if the handshake is successful then there will be no response
        # Handshake request will be determined "failed" if the server terminates the connection

        if not len(message["user"]) in range(1, 21):
            await client.close(code=self.supporter.connection_error, reason=f"Invalid username: {message['user']}")
            return

        if not len(message["project_id"]) in range(1, 101):
            await client.close(code=self.supporter.connection_error, reason=f"Invalid room ID: {message['project_id']}")
            return

        if not len(message["project_id"]) in range(1, 101):
            await client.close(code=self.supporter.connection_error, reason=f"Invalid room ID: {message['project_id']}")
            return

        if ("scratchsessionsid" in client.request_headers) or ("scratchsessionsid" in client.response_headers):
            await client.send(
                "The cloud data library you are using is putting your Scratch account at risk by sending us your login token for no reason. Change your Scratch password immediately, then contact the maintainers of that library for further information. This connection is being refused to protect your security.")
            await self.parent.asyncio.sleep(0.1)
            await client.close(code=self.supporter.refused_security, reason=f"Connection closed for security reasons")
            return

        # Create the project room
        if not self.parent.rooms.exists(message["project_id"]):
            self.parent.rooms.create(message["project_id"])

        # Get the room data
        room = self.parent.rooms.get(message["project_id"])

        # Add the user to the room
        room.users.add(client)

        # Configure the client
        client.rooms = [message["project_id"]]

        result = self.parent.clients.set_username(client, message["user"])
        if result != self.supporter.username_set:
            await client.close(code=self.supporter.username_error, reason=f"Username conflict")
            return

        if client.friendly_username in room.usernames:
            await client.close(code=self.supporter.username_error, reason=f"Username conflict")
            return

        room.usernames.add(client.friendly_username)

        # Sync the global variable state
        room = self.parent.rooms.get(client.rooms[0])
        if len(room.global_vars.keys()) != 0:
            # Wait for client to finish processing new state
            await self.parent.asyncio.sleep(0.1)

            # Update the client's state
            for var in room.global_vars.keys():
                message = {
                    "method": "set",
                    "name": var,
                    "value": room.global_vars[var]
                }
                await client.send(self.json.dumps(message))

    async def set(self, client, message):
        # Validate the message syntax and datatypes
        if not await self.__auto_validate__(self.validator[self.set], client, message):
            return

        room = self.parent.rooms.get(client.rooms[0])
        if not room:
            await client.close(code=self.supporter.connection_error, reason="No room set up yet")
            return
        else:
            # Don't update the value if it's already set
            if message["name"] in room.global_vars:
                if room.global_vars[message["name"]] == message["value"]:
                    return

            room.global_vars[message["name"]] = message["value"]
            await self.send_packet_multicast_variable(
                cmd="set",
                name=message["name"],
                val=message["value"],
                room_id=client.rooms[0]
            )

    async def create(self, client, message):
        # Validate the message syntax and datatypes
        if not await self.__auto_validate__(self.validator[self.create], client, message):
            return

        room = self.parent.rooms.get(client.rooms[0])
        if not room:
            await client.close(code=self.supporter.connection_error, reason="No room set up yet")
            return
        else:
            if message["name"] in room.global_vars:
                return

            room.global_vars[message["name"]] = message["value"]
            await self.send_packet_multicast_variable(
                cmd="create",
                name=message["name"],
                val=message["value"],
                room_id=client.rooms[0]
            )

    async def delete(self, client, message):
        # Validate the message syntax and datatypes
        if not await self.__auto_validate__(self.validator[self.delete], client, message):
            return

        room = self.parent.rooms.get(client.rooms[0])
        if not room:
            await client.close(code=self.supporter.connection_error, reason="No room set up yet")
            return
        else:
            if not message["name"] in room.global_vars:
                return

            del room.global_vars[message["name"]]
            await self.send_packet_multicast_variable(
                cmd="delete",
                name=message["name"],
                room_id=client.rooms[0]
            )

    async def rename(self, client, message):
        # Validate the message syntax and datatypes
        if not await self.__auto_validate__(self.validator[self.rename], client, message):
            return

        room = self.parent.rooms.get(client.rooms[0])

        if not room:
            await client.close(code=self.supporter.connection_error, reason="No room set up yet")
            return
        else:
            if not message["name"] in room.global_vars:
                await client.close(code=self.supporter.connection_error, reason="Variable does not exist")
                return

            # Copy the old room data to new one, and then delete
            room.global_vars[message["new_name"]] = self.copy(room.global_vars[message["name"]])
            del room.global_vars[message["name"]]

            await self.send_packet_multicast_variable(
                cmd="rename",
                name=message["name"],
                new_name=message["new_name"],
                room_id=client.rooms[0]
            )
