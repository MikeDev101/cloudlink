"""
This is the default protocol used for the CloudLink client.
The CloudLink 4.1 Protocol retains full support for CLPv4.

Each packet format is compliant with UPLv2 formatting rules.

Documentation for the CLPv4.1 protocol can be found here:
https://hackmd.io/@MikeDEV/HJiNYwOfo
"""


class clpv4:
    def __init__(self, parent):

        # Define various status codes for the protocol.
        class statuscodes:
            # Code type character
            info = "I"
            error = "E"

            # Error / info codes as tuples
            test = (info, 0, "Test")
            echo = (info, 1, "Echo")
            ok = (info, 100, "OK")
            syntax = (error, 101, "Syntax")
            datatype = (error, 102, "Datatype")
            id_not_found = (error, 103, "ID not found")
            id_not_specific = (error, 104, "ID not specific enough")
            internal_error = (error, 105, "Internal server error")
            empty_packet = (error, 106, "Empty packet")
            id_already_set = (error, 107, "ID already set")
            refused = (error, 108, "Refused")
            invalid_command = (error, 109, "Invalid command")
            disabled_command = (error, 110, "Command disabled")
            id_required = (error, 111, "ID required")
            id_conflict = (error, 112, "ID conflict")
            too_large = (error, 113, "Too large")
            json_error = (error, 114, "JSON error")
            room_not_joined = (error, 115, "Room not joined")

        # Generate a user object
        def generate_user_object():
            # Username set
            if parent.client.username_set:
                return {
                    "id": parent.client.snowflake,
                    "username": parent.client.username,
                    "uuid": str(parent.client.id)
                }

            # Username not set
            return {
                "id": parent.client.snowflake,
                "uuid": str(parent.client.id)
            }

        # Expose username object generator function for extension usage
        self.generate_user_object = generate_user_object

        async def set_username(username):
            parent.logger.debug(f"Setting username to {username}...")

            # Send the set username request with a listener and wait for a response
            response = await parent.send_packet_and_wait({
                "cmd": "setid",
                "val": username,
                "listener": "init_username"
            })

            if response["code_id"] == statuscodes.ok[1]:
                # Log the successful connection
                parent.logger.info(f"Successfully set username to {username}.")

                # Fire all on_connect events
                val = response["val"]
                parent.asyncio.create_task(
                    parent.execute_on_username_set_events(val["id"], val["username"], val["uuid"])
                )

            else:
                # Log the connection error
                parent.logger.error(f"Failed to set username. Got response code: {response['code']}")

        # Expose the username set command
        self.set_username = set_username

        # The CLPv4 command set
        @parent.on_initial_connect
        async def on_initial_connect():
            parent.logger.debug("Performing handshake with the server...")

            # Send the handshake request with a listener and wait for a response
            response = await parent.send_packet_and_wait({
                "cmd": "handshake",
                "val": {
                    "language": "Python",
                    "version": parent.version
                },
                "listener": "init_handshake"
            })

            if response["code_id"] == statuscodes.ok[1]:
                # Log the successful connection
                parent.logger.info("Successfully connected to the server.")

                # Fire all on_connect events
                parent.asyncio.create_task(
                    parent.execute_on_full_connect_events()
                )

            else:
                # Log the connection error
                parent.logger.error(f"Failed to connect to the server. Got response code: {response['code']}")

                # Disconnect
                parent.asyncio.create_task(
                    parent.disconnect()
                )

        @parent.on_command(cmd="ping")
        async def on_ping(message):
            events = [event(message) for event in parent.protocol_command_handlers["ping"]]
            group = parent.asyncio.gather(*events)
            await group

        @parent.on_command(cmd="gmsg")
        async def on_gmsg(message):
            events = [event(message) for event in parent.protocol_command_handlers["gmsg"]]
            group = parent.asyncio.gather(*events)
            await group

        @parent.on_command(cmd="pmsg")
        async def on_pmsg(message):
            events = [event(message) for event in parent.protocol_command_handlers["pmsg"]]
            group = parent.asyncio.gather(*events)
            await group

        @parent.on_command(cmd="gvar")
        async def on_gvar(message):
            events = [event(message) for event in parent.protocol_command_handlers["gvar"]]
            group = parent.asyncio.gather(*events)
            await group

        @parent.on_command(cmd="pvar")
        async def on_pvar(message):
            events = [event(message) for event in parent.protocol_command_handlers["pvar"]]
            group = parent.asyncio.gather(*events)
            await group

        @parent.on_command(cmd="statuscode")
        async def on_statuscode(message):
            events = [event(message) for event in parent.protocol_command_handlers["statuscode"]]
            group = parent.asyncio.gather(*events)
            await group

        @parent.on_command(cmd="client_obj")
        async def on_client_obj(message):
            parent.logger.info(f"This client is known as ID {message['val']['id']} with UUID {message['val']['uuid']}.")

        @parent.on_command(cmd="client_ip")
        async def on_client_ip(message):
            parent.logger.debug(f"Client IP address is {message['val']}")

        @parent.on_command(cmd="server_version")
        async def on_server_version(message):
            parent.logger.info(f"Server is running Cloudlink v{message['val']}.")

        @parent.on_command(cmd="ulist")
        async def on_ulist(message):
            events = [event(message) for event in parent.protocol_command_handlers["ulist"]]
            group = parent.asyncio.gather(*events)
            await group

        @parent.on_command(cmd="direct")
        async def on_direct(message):
            events = [event(message) for event in parent.protocol_command_handlers["direct"]]
            group = parent.asyncio.gather(*events)
            await group
