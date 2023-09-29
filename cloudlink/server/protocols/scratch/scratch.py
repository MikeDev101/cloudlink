from .schema import scratch_protocol

"""
This is a FOSS reimplementation of Scratch's Cloud Variable protocol.
See https://github.com/TurboWarp/cloud-server/blob/master/doc/protocol.md for details.
"""


class scratch:
    def __init__(self, server):
        self.__qualname__ = "scratch"

        # Define various status codes for the protocol.
        class statuscodes:
            connection_error = 4000
            username_error = 4002
            overloaded = 4003
            unavailable = 4004
            refused_security = 4005

        # Exposes the schema of the protocol.
        self.schema = scratch

        # valid(message, schema): Used to verify messages.
        def valid(client, message, schema, allow_unknown=True):
            validator = server.validator(schema, allow_unknown=allow_unknown)
            
            if validator.validate(message):
                return True
            else:
                errors = validator.errors
                server.logger.warning(f"Error: {errors}")
                server.send_packet_unicast(client, f"Validation failed: {dict(errors)}")
                server.close_connection(client, code=statuscodes.connection_error, reason=f"Validation failed")
                return False

        @server.on_protocol_disconnect(schema=scratch_protocol)
        async def protocol_disconnect(client):
            server.logger.debug(f"Removing client {client.snowflake} from rooms...")

            # Unsubscribe from all rooms
            async for room_id in server.async_iterable(server.copy(client.rooms)):
                server.rooms_manager.unsubscribe(client, room_id)

        @server.on_command(cmd="handshake", schema=scratch_protocol)
        async def handshake(client, message):

            # Don't execute this command if handshake was already done
            if client.handshake:
                return
            client.handshake = True

            # Safety first
            if ("scratchsessionsid" in client.request_headers) or ("scratchsessionsid" in client.response_headers):

                # Log the hiccup
                server.logger.critical(f"Client {client.id} sent scratchsessionsid header(s) - Aborting connection!")

                # Tell the client they are doing a no-no
                server.send_packet_unicast(client, "The cloud data library you are using is putting your Scratch account at risk by sending your login token for no reason. Change your Scratch password immediately, then contact the maintainers of that library for further information. This connection is being closed to protect your security.")

                # Abort the connection
                server.close_connection(client, code=statuscodes.refused_security, reason=f"Connection closed for security reasons")

                # End this guard clause
                return

            # Validate schema
            if not valid(client, message, scratch_protocol.handshake):
                return

            # Set username
            server.logger.debug(f"Scratch client {client.snowflake} declares username {message['user']}.")

            # Set client username
            server.clients_manager.set_username(client, message['user'])

            # Subscribe to room
            server.rooms_manager.subscribe(client, message["project_id"])

            # Get values
            room_data = server.rooms_manager.get(message["project_id"])

            # Sync project ID variable state
            server.logger.debug(f"Synchronizing room {message['project_id']} state to client {client.id}")
            async for variable in server.async_iterable(room_data["global_vars"]):
                server.send_packet_unicast(client, {
                    "method": "set",
                    "name": variable,
                    "value": room_data["global_vars"][variable]
                })

        @server.on_command(cmd="create", schema=scratch_protocol)
        async def create_variable(client, message):

            # Don't execute this command if handshake wasn't already done
            if not client.handshake:
                return

            # Validate schema
            if not valid(client, message, scratch_protocol.method):
                return

            # Guard clause - Room must exist before adding to it
            if not server.rooms_manager.exists(message["project_id"]):
                server.logger.warning(f"Error: room {message['project_id']} does not exist yet")

                # Abort the connection
                server.close_connection(client, code=statuscodes.unavailable, reason=f"Invalid room ID: {message['project_id']}")

            server.logger.debug(f"Creating global variable {message['name']} in {message['project_id']}")

            # Get values
            room_data = server.rooms_manager.get(message["project_id"])

            # Create variable
            room_data["global_vars"][message['name']] = message["value"]

            # Broadcast the variable state
            server.send_packet_multicast(room_data["clients"][scratch_protocol]["all"], {
                "method": "create",
                "name": message['name'],
                "value": room_data["global_vars"][message['name']]
            })

        @server.on_command(cmd="rename", schema=scratch_protocol)
        async def rename_variable(client, message):

            # Don't execute this command if handshake wasn't already done
            if not client.handshake:
                return

            # Validate schema
            if not valid(client, message, scratch_protocol.method):
                return

            # Guard clause - Room must exist before deleting values from it
            if not server.rooms_manager.exists(message["project_id"]):
                server.logger.warning(f"Error: room {message['project_id']} does not exist yet")
                
                # Abort the connection
                server.close_connection(
                    client,
                    code=statuscodes.unavailable,
                    reason=f"Invalid room ID: {message['project_id']}"
                )
                return

            server.logger.debug(f"Renaming global variable {message['name']} to {message['new_name']} in {message['project_id']}")

            # Get values
            room_data = server.rooms_manager.get(message["project_id"])

            if message["name"] in room_data["global_vars"]:
                # Copy variable
                room_data["global_vars"][message["new_name"]] = server.copy(room_data["global_vars"][message["name"]])

                # Delete old variable
                room_data["global_vars"].pop(message['name'])
            else:
                # Create new variable (renamed from a value in a deleted room)
                room_data["global_vars"][message["new_name"]] = str()

            # Broadcast the variable state
            server.send_packet_multicast(room_data["clients"][scratch_protocol]["all"], {
                "method": "rename",
                "name": message['name'],
                "new_name": message['new_name']
            })

        @server.on_command(cmd="delete", schema=scratch_protocol)
        async def create_variable(client, message):

            # Don't execute this command if handshake wasn't already done
            if not client.handshake:
                return

            # Validate schema
            if not valid(client, message, scratch_protocol.method):
                return

            # Guard clause - Room must exist before deleting values from it
            if not server.rooms_manager.exists(message["project_id"]):
                server.logger.warning(f"Error: room {message['project_id']} does not exist yet")
                
                # Abort the connection
                server.close_connection(
                    client,
                    code=statuscodes.unavailable,
                    reason=f"Invalid room ID: {message['project_id']}"
                )
                return

            server.logger.debug(f"Deleting global variable {message['name']} in {message['project_id']}")

            # Get values
            room_data = server.rooms_manager.get(message["project_id"])

            # Delete variable
            room_data["global_vars"].pop(message['name'])

            # Broadcast the variable state
            server.send_packet_multicast(room_data["clients"][scratch_protocol]["all"], {
                "method": "delete",
                "name": message['name']
            })

        @server.on_command(cmd="set", schema=scratch_protocol)
        async def set_value(client, message):

            # Don't execute this command if handshake wasn't already done
            if not client.handshake:
                return

            # Validate schema
            if not valid(client, message, scratch_protocol.method):
                return

            # Guard clause - Room must exist before adding to it
            if not server.rooms_manager.exists(message["project_id"]):
                server.logger.warning(f"Error: room {message['project_id']} does not exist yet")
                
                # Abort the connection
                server.close_connection(
                    client,
                    code=statuscodes.unavailable,
                    reason=f"Invalid room ID: {message['project_id']}"
                )
                return

            # Get values
            room_data = server.rooms_manager.get(message["project_id"])

            # Don't re-broadcast values that are identical
            if message["name"] in room_data["global_vars"]:
                if room_data["global_vars"][message['name']] == message["value"]:
                    server.logger.debug(f"Not going to rebroadcast global variable {message['name']} in {message['project_id']}")
                    return

            server.logger.debug(f"Updating global variable {message['name']} in {message['project_id']} to value {message['value']}")

            # Update variable
            room_data["global_vars"][message['name']] = message["value"]

            # Broadcast the variable state
            server.send_packet_multicast(room_data["clients"][scratch_protocol]["all"], {
                "method": "set",
                "name": message['name'],
                "value": room_data["global_vars"][message['name']]
            })
