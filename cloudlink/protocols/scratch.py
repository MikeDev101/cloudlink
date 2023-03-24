"""
This is a FOSS reimplementation of Scratch's Cloud Variable protocol.
See https://github.com/TurboWarp/cloud-server/blob/master/doc/protocol.md for details.
"""


class scratch:
    def __init__(self, server):

        # Define various status codes for the protocol.
        class statuscodes:
            connection_error = 4000
            username_error = 4002
            overloaded = 4003
            unavailable = 4004
            refused_security = 4005

        # protocol_schema: The default schema to identify the protocol.
        self.protocol_schema = server.schemas.scratch

        # valid(message, schema): Used to verify messages.
        def valid(client, message, schema):
            if server.validator(message, schema):
                return True
            else:
                errors = server.validator.errors
                server.logger.warning(f"Error: {errors}")
                server.close_connection(client, code=statuscodes.connection_error, reason=f"Message schema validation failed")
                return False

        @server.on_command(cmd="handshake", schema=self.protocol_schema)
        async def handshake(client, message):

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

            # Create project ID (temporary since rooms_manager isn't done yet)
            if not message["project_id"] in self.storage:
                self.storage[message["project_id"]] = dict()

            # Sync project ID variable state
            for variable in self.storage[message["project_id"]]:
                server.logger.debug(f"Sending variable {variable} to client {client.id}")
                server.send_packet_unicast(client, {
                    "method": "set",
                    "name": variable,
                    "value": self.storage[message["project_id"]][variable]
                })

        @server.on_command(cmd="create", schema=self.protocol_schema)
        async def create_variable(client, message):

            # Validate schema
            if not valid(client, message, self.protocol_schema.method):
                return

            # Guard clause - Room must exist before adding to it
            if not message["project_id"] in self.storage:
                server.logger.warning(f"Error: room {message['project_id']} does not exist yet")

                # Abort the connection
                server.close_connection(client, code=statuscodes.unavailable, reason=f"Invalid room ID: {message['project_id']}")

            server.logger.debug(f"Creating global variable {message['name']} in {message['project_id']}")

            # Create the variable
            self.storage[message["project_id"]][message['name']] = message["value"]

            # Broadcast the variable
            for variable in self.storage[message["project_id"]]:
                server.logger.debug(f"Creating variable {variable} in {len(server.clients_manager)} clients")
                server.send_packet_multicast(server.clients_manager.clients, {
                    "method": "create",
                    "name": variable,
                    "value": self.storage[message["project_id"]][variable]
                })

        @server.on_command(cmd="rename", schema=self.protocol_schema)
        async def rename_variable(client, message):

            # Validate schema
            if not valid(client, message, self.protocol_schema.method):
                return

        @server.on_command(cmd="delete", schema=self.protocol_schema)
        async def create_variable(client, message):

            # Validate schema
            if not valid(client, message, self.protocol_schema.method):
                return

            # Guard clause - Room must exist before deleting values from it
            if not message["project_id"] in self.storage:
                server.logger.warning(f"Error: room {message['project_id']} does not exist yet")

                # Abort the connection
                server.close_connection(client, code=statuscodes.unavailable, reason=f"Invalid room ID: {message['project_id']}")

            server.logger.debug(f"Deleting global variable {message['name']} in {message['project_id']}")

            # Delete the variable
            del self.storage[message["project_id"]][message['name']]

            # Broadcast the variable
            for variable in self.storage[message["project_id"]]:
                server.logger.debug(f"Deleting variable {variable} in {len(server.clients_manager)} clients")
                server.send_packet_multicast(server.clients_manager.clients, {
                    "method": "delete",
                    "name": variable
                })

        @server.on_command(cmd="set", schema=self.protocol_schema)
        async def set_value(client, message):

            # Validate schema
            if not valid(client, message, self.protocol_schema.method):
                return

            # Guard clause - Room must exist before adding to it
            if not message["project_id"] in self.storage:

                # Abort the connection
                server.close_connection(client, code=statuscodes.unavailable, reason=f"Invalid room ID: {message['project_id']}")

            server.logger.debug(f"Updating global variable {message['name']} to value {message['value']}")

            # Update variable state
            self.storage[message["project_id"]][message['name']] = message['value']

            # Broadcast the variable
            for variable in self.storage[message["project_id"]]:
                server.logger.debug(f"Sending variable {variable} to {len(server.clients_manager)} clients")
                server.send_packet_multicast(server.clients_manager.clients, {
                    "method": "set",
                    "name": variable,
                    "value": self.storage[message["project_id"]][variable]
                })
