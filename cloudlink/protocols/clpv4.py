"""
This is the default protocol used for the CloudLink server.
The CloudLink 4.1 Protocol retains full support for CLPv4.

Each packet format is compliant with UPLv2 formatting rules.

Documentation for the CLPv4.1 protocol can be found here:
https://hackmd.io/@MikeDEV/HJiNYwOfo
"""

class clpv4:
    def __init__(self, server):

        # protocol_schema: The default schema to identify the protocol.
        self.protocol = server.schemas.clpv4

        # valid(message, schema): Used to verify messages.
        def valid(client, message, schema):
            if server.validator(message, schema):
                return True
            else:
                errors = server.validator.errors
                server.logger.debug(f"Error: {errors}")
                server.send_packet(client, {
                    "cmd": "statuscode",
                    "code": "error",
                    "code_id": 1234,
                    "details": dict(errors)
                })
                return False

        @server.on_exception(exception_type=server.exceptions.InvalidCommand, schema=self.protocol)
        async def invalid_command(client, details):
            server.send_packet(client, {
                "cmd": "statuscode",
                "code": "error",
                "code_id": 1234,
                "details": details
            })

        @server.on_exception(exception_type=server.exceptions.JSONError, schema=self.protocol)
        async def json_exception(client, details):
            server.send_packet(client, {
                "cmd": "statuscode",
                "code": "error",
                "code_id": 1234,
                "details": details
            })

        @server.on_exception(exception_type=server.exceptions.EmptyMessage, schema=self.protocol)
        async def empty_message(client, details):
            server.send_packet(client, {
                "cmd": "statuscode",
                "code": "error",
                "code_id": 1234,
                "details": details
            })

        @server.on_command(cmd="handshake", schema=self.protocol)
        async def on_handshake(client, message):
            # Send client IP address
            server.send_packet(client, {
                "cmd": "client_ip",
                "val": client.remote_address[0]
            })

            # Send server version
            server.send_packet(client, {
                "cmd": "server_version",
                "val": server.version
            })

            # Send Message-Of-The-Day
            if server.enable_motd:
                server.send_packet(client, {
                    "cmd": "motd",
                    "val": server.motd_message
                })

            # Send client's Snowflake ID
            server.send_packet(client, {
                "cmd": "client_id",
                "val": client.snowflake
            })

            # Define status message
            tmp_message = {
                "cmd": "statuscode",
                "val": "ok"
            }

            # Attach listener
            if "listener" in message:
                tmp_message["listener"] = message["listener"]

            # Return ping
            server.send_packet(client, tmp_message)

        @server.on_command(cmd="ping", schema=self.protocol)
        async def on_ping(client, message):

            # Define message
            tmp_message = {
                "cmd": "statuscode",
                "val": "ok"
            }

            # Attach listener
            if "listener" in message:
                tmp_message["listener"] = message["listener"]

            # Return ping
            server.send_packet(client, tmp_message)

        @server.on_command(cmd="gmsg", schema=self.protocol)
        async def on_gmsg(client, message):

            # Validate schema
            if not valid(client, message, self.protocol.gmsg):
                return

            # Copy the current set of connected client objects
            clients = server.copy(server.clients_manager.protocols[self.protocol])

            # Attach listener (if present) and broadcast
            if "listener" in message:

                # Remove originating client from broadcast
                clients.remove(client)

                # Define the message to broadcast
                tmp_message = {
                    "cmd": "gmsg",
                    "val": message["val"]
                }

                # Broadcast message
                server.send_packet(clients, tmp_message)

                # Define the message to send
                tmp_message = {
                    "cmd": "gmsg",
                    "val": message["val"],
                    "listener": message["listener"]
                }

                # Unicast message
                server.send_packet(client, tmp_message)
            else:
                # Define the message to broadcast
                tmp_message = {
                    "cmd": "gmsg",
                    "val": message["val"]
                }

                # Broadcast message
                server.send_packet(clients, tmp_message)

        @server.on_command(cmd="pmsg", schema=self.protocol)
        async def on_pmsg(client, message):

            tmp_client = None

            # Validate schema
            if not valid(client, message, self.protocol.pmsg):
                return

            # Find client
            try:
                tmp_client = server.clients_manager.find_obj(message['id'])
            except server.clients_manager.exceptions.NoResultsFound:
                server.send_packet(client, {
                    "cmd": "statuscode",
                    "code": "error",
                    "code_id": 1234,
                    "details": f'No matches found: {message["id"]}'
                })

            # Broadcast message to client
            tmp_message = {
                "cmd": "pmsg",
                "val": message["val"],
                "origin": {
                    "id": client.snowflake,
                    "username": client.friendy_username
                }
            }

            # Send private message
            server.send_packet(tmp_client, tmp_message)

        @server.on_command(cmd="gvar", schema=self.protocol)
        async def on_gvar(client, message):

            # Validate schema
            if not valid(client, message, self.protocol.gvar):
                return

            # Define the message to send
            tmp_message = {
                "cmd": "gvar",
                "name": message["name"],
                "val": message["val"]
            }

            # Copy the current set of connected client objects
            clients = server.copy(server.clients_manager.protocols[self.protocol])

            # Attach listener (if present) and broadcast
            if "listener" in message:
                clients.remove(client)
                server.send_packet(clients, tmp_message)
                tmp_message["listener"] = message["listener"]
                server.send_packet(client, tmp_message)
            else:
                server.send_packet(clients, tmp_message)

        @server.on_command(cmd="pvar", schema=self.protocol)
        async def on_pvar(client, message):
            tmp_client = None

            # Validate schema
            if not valid(client, message, self.protocol.pvar):
                return

            # Find client
            try:
                tmp_client = server.clients_manager.find_obj(message['id'])
            except server.clients_manager.exceptions.NoResultsFound:
                server.send_packet(client, {
                    "cmd": "statuscode",
                    "code": "error",
                    "code_id": 1234,
                    "details": f'No matches found: {message["id"]}'
                })

            # Broadcast message to client
            tmp_message = {
                "cmd": "pvar",
                "name": message["name"],
                "val": message["val"],
                "origin": {
                    "id": client.snowflake,
                    "username": client.friendy_username
                }
            }

            server.send_packet(client, tmp_message)

        @server.on_command(cmd="setid", schema=self.protocol)
        async def on_setid(client, message):
            # Validate schema
            if not valid(client, message, self.protocol.setid):
                return

            try:
                server.clients_manager.set_username(client, message['val'])
            except server.clients_manager.exceptions.ClientUsernameAlreadySet:
                server.logger.error(f"Client {client.snowflake} attempted to set username again!")
                return

            tmp_message = {
                "cmd": "statuscode",
                "val": {
                    "id": client.snowflake,
                    "username": client.friendy_username
                },
                "code": "error",
                "code_id": 1234
            }

            # Attach listener (if present) and broadcast
            if "listener" in message:
                tmp_message["listener"] = message["listener"]
                server.send_packet(client, tmp_message)
            else:
                server.send_packet(client, tmp_message)

        @server.on_command(cmd="link", schema=self.protocol)
        async def on_link(client, message):
            server.rooms_manager.subscribe(client, message["rooms"])

        @server.on_command(cmd="unlink", schema=self.protocol)
        async def on_unlink(client, message):
            pass

        @server.on_command(cmd="direct", schema=self.protocol)
        async def on_direct(client, message):
            pass

        @server.on_command(cmd="bridge", schema=self.protocol)
        async def on_bridge(client, message):
            pass
        
        @server.on_command(cmd="echo", schema=self.protocol)
        async def on_echo(client, message):
            server.send_packet(client, {"cmd": "echo", "val": message["val"]})
