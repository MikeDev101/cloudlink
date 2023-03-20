class clpv4:
    def __init__(self, server):

        # protocol_schema: The default schema to identify the protocol.
        self.protocol_schema = server.schemas.clpv4

        # valid(message, schema): Used to verify messages.
        def valid(client, message, schema):
            if server.validator(message, schema):
                return True
            else:
                errors = server.validator.errors
                server.logger.debug(f"Error: {errors}")
                server.send_packet(client, {
                    "cmd": "statuscode",
                    "val": "error",
                    "details": dict(errors)
                })
                return False

        @server.on_exception(exception_type=server.exceptions.InvalidCommand, schema=self.protocol_schema)
        async def exception_handler(client, details):
            server.send_packet(client, {
                "cmd": "statuscode",
                "val": "error",
                "details": details
            })

        @server.on_exception(exception_type=server.exceptions.JSONError, schema=self.protocol_schema)
        async def exception_handler(client, details):
            server.send_packet(client, {
                "cmd": "statuscode",
                "val": "error",
                "details": details
            })

        @server.on_exception(exception_type=server.exceptions.EmptyMessage, schema=self.protocol_schema)
        async def exception_handler(client, details):
            server.send_packet(client, {
                "cmd": "statuscode",
                "val": "error",
                "details": details
            })

        @server.on_command(cmd="handshake", schema=self.protocol_schema)
        async def on_handshake(client, message):
            server.send_packet(client, {
                "cmd": "client_ip",
                "val": client.remote_address[0]
            })

            server.send_packet(client, {
                "cmd": "server_version",
                "val": server.version
            })

            if server.enable_motd:
                server.send_packet(client, {
                    "cmd": "motd",
                    "val": server.motd_message
                })

            server.send_packet(client, {
                "cmd": "client_id",
                "val": client.snowflake
            })

            server.send_packet(client, {
                "cmd": "statuscode",
                "val": "ok"
            })

        @server.on_command(cmd="ping", schema=self.protocol_schema)
        async def on_ping(client, message):
            server.send_packet(client, {
                "cmd": "statuscode",
                "val": "ok"
            })

        @server.on_command(cmd="gmsg", schema=self.protocol_schema)
        async def on_gmsg(client, message):

            # Validate schema
            if not valid(client, message, self.protocol_schema.gmsg):
                return

            # Copy the current set of connected client objects
            clients = server.copy(server.clients_manager.protocols[self.protocol_schema])

            # Attach listener (if present) and broadcast
            if "listener" in message:

                # Remove originating client from broadcast
                clients.remove(client)

                # Define the message to broadcast
                tmp_message = {
                    "cmd": "gmsg",
                    "val": message["val"]
                }
                server.send_packet(clients, tmp_message)

                # Send message to originating client with listener
                # Define the message to send
                tmp_message = {
                    "cmd": "gmsg",
                    "val": message["val"],
                    "listener": message["listener"]
                }
                server.send_packet(client, tmp_message)
            else:
                # Broadcast message to all clients
                tmp_message = {
                    "cmd": "gmsg",
                    "val": message["val"]
                }
                server.send_packet(clients, tmp_message)

        @server.on_command(cmd="pmsg", schema=self.protocol_schema)
        async def on_pmsg(client, message):

            tmp_client = None

            # Validate schema
            if not valid(client, message, self.protocol_schema.pmsg):
                return

            # Find client
            try:
                tmp_client = server.clients_manager.find_obj(message['id'])
            except server.clients_manager.exceptions.NoResultsFound:
                server.send_packet(client, {
                    "cmd": "statuscode",
                    "val": "notfound",
                    "details": f'No matches found: {message["id"]}'
                })

            # Broadcast message to client
            tmp_message = {
                "cmd": "pmsg",
                "val": message["val"],
                "origin": client.snowflake
            }

            # Send private message
            server.send_packet(tmp_client, tmp_message)

        @server.on_command(cmd="gvar", schema=self.protocol_schema)
        async def on_gvar(client, message):

            # Validate schema
            if not valid(client, message, self.protocol_schema.gvar):
                return

            # Define the message to send
            tmp_message = {
                "cmd": "gvar",
                "name": message["name"],
                "val": message["val"]
            }

            # Copy the current set of connected client objects
            clients = server.copy(server.clients_manager.protocols[self.protocol_schema])

            # Attach listener (if present) and broadcast
            if "listener" in message:
                clients.remove(client)
                server.send_packet(clients, tmp_message)
                tmp_message["listener"] = message["listener"]
                server.send_packet(client, tmp_message)
            else:
                server.send_packet(clients, tmp_message)

        @server.on_command(cmd="pvar", schema=self.protocol_schema)
        async def on_pvar(client, message):
            print("Private variables!")

        @server.on_command(cmd="setid", schema=self.protocol_schema)
        async def on_setid(client, message):
            try:
                server.clients_manager.set_username(client, message['val'])
            except server.clients_manager.exceptions.ClientUsernameAlreadySet:
                server.logger.error(f"Client {client.snowflake} attempted to set username again!")

        @server.on_command(cmd="link", schema=self.protocol_schema)
        async def on_link(client, message):
            pass

        @server.on_command(cmd="unlink", schema=self.protocol_schema)
        async def on_unlink(client, message):
            pass

        @server.on_command(cmd="direct", schema=self.protocol_schema)
        async def on_direct(client, message):
            pass

        @server.on_command(cmd="bridge", schema=self.protocol_schema)
        async def on_bridge(client, message):
            pass
        
        @server.on_command(cmd="echo", schema=self.protocol_schema)
        async def on_echo(client, message):
            server.send_packet(client, {"cmd": "echo", "val": message["val"]})
