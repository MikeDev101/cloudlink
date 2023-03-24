"""
This is the default protocol used for the CloudLink server.
The CloudLink 4.1 Protocol retains full support for CLPv4.

Each packet format is compliant with UPLv2 formatting rules.

Documentation for the CLPv4.1 protocol can be found here:
https://hackmd.io/@MikeDEV/HJiNYwOfo
"""


class clpv4:
    def __init__(self, server):
        # Configuration settings

        # Warn origin client if it's attempting to send messages using a username that resolves more than one client.
        self.warn_if_multiple_username_matches = True

        # Message of the day
        self.enable_motd = False
        self.motd_message = str()

        # protocol_schema: The default schema to identify the protocol.
        self.protocol = server.schemas.clpv4

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

            @staticmethod
            def generate(code: tuple):
                return f"{code[0]}:{code[1]} | {code[2]}", code[1]

        # Identification of a client's IP address
        def get_client_ip(client):
            # Grab forwarded IP address
            if "x-forwarded-for" in client.request_headers:
                return client.request_headers.get("x-forwarded-for")

            # Grab Cloudflare IP address
            if "cf-connecting-ip" in client.request_headers:
                return client.request_headers.get("cf-connecting-ip")

            # Grab host address, ignoring port info
            if type(client.remote_address) == tuple:
                return str(client.remote_address[0])

            # Default if none of the above work
            return client.remote_address

        # valid(message, schema): Used to verify messages.
        def valid(client, message, schema):
            if server.validator(message, schema):
                return True

            # Alert the client that the schema was invalid
            send_statuscode(client, statuscodes.syntax, details=dict(server.validator.errors))
            return False

        # Simplify sending error/info messages
        def send_statuscode(client, code, details=None, listener=None, val=None):
            # Generate a statuscode
            code_human, code_id = statuscodes.generate(code)

            # Template the message
            tmp_message = {
                "cmd": "statuscode",
                "code": code_human,
                "code_id": code_id
            }

            if details:
                tmp_message["details"] = details

            if listener:
                tmp_message["listener"] = listener

            if val:
                tmp_message["val"] = val

            # Send the code
            server.send_packet(client, tmp_message)

        # Exception handlers

        @server.on_exception(exception_type=server.exceptions.ValidationError, schema=self.protocol)
        async def validation_failure(client, details):
            send_statuscode(client, statuscodes.syntax, details=dict(details))

        @server.on_exception(exception_type=server.exceptions.InvalidCommand, schema=self.protocol)
        async def invalid_command(client, details):
            send_statuscode(
                client,
                statuscodes.invalid_command,
                details=f"{details} is an invalid command."
            )

        @server.on_disabled_command(schema=self.protocol)
        async def disabled_command(client, details):
            send_statuscode(
                client,
                statuscodes.disabled_command,
                details=f"{details} is a disabled command."
            )

        @server.on_exception(exception_type=server.exceptions.JSONError, schema=self.protocol)
        async def json_exception(client, details):
            send_statuscode(
                client,
                statuscodes.json_error,
                details=f"A JSON error was raised: {details}"
            )

        @server.on_exception(exception_type=server.exceptions.EmptyMessage, schema=self.protocol)
        async def empty_message(client, details):
            send_statuscode(
                client,
                statuscodes.empty_packet,
                details="Your client has sent an empty message."
            )

        # The CLPv4 command set

        @server.on_command(cmd="handshake", schema=self.protocol)
        async def on_handshake(client, message):
            # Send client IP address
            server.send_packet(client, {
                "cmd": "client_ip",
                "val": get_client_ip(client)
            })

            # Send server version
            server.send_packet(client, {
                "cmd": "server_version",
                "val": server.version
            })

            # Send Message-Of-The-Day
            if self.enable_motd:
                server.send_packet(client, {
                    "cmd": "motd",
                    "val": self.motd_message
                })

            # Send client's Snowflake ID
            server.send_packet(client, {
                "cmd": "client_id",
                "val": client.snowflake
            })

            # Attach listener
            if "listener" in message:
                send_statuscode(client, statuscodes.ok, listener=message["listener"])
            else:
                send_statuscode(client, statuscodes.ok)

        @server.on_command(cmd="ping", schema=self.protocol)
        async def on_ping(client, message):
            listener = None

            if "listener" in message:
                listener = message["listener"]

            send_statuscode(client, statuscodes.ok, listener=listener)

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
            # Require sending client to have set their username
            if not client.username_set:
                # Attach listener
                if "listener" in message:
                    send_statuscode(
                        client,
                        statuscodes.id_required,
                        details="This command requires setting a username.",
                        listener=message["listener"]
                    )
                else:
                    send_statuscode(
                        client,
                        statuscodes.id_required,
                        details="This command requires setting a username."
                    )

                # End pmsg command handler
                return

            tmp_client = None

            # Validate schema
            if not valid(client, message, self.protocol.pmsg):
                return

            # Find client
            try:
                tmp_client = server.clients_manager.find_obj(message['id'])

            # No objects found
            except server.clients_manager.exceptions.NoResultsFound:

                # Attach listener
                if "listener" in message:
                    send_statuscode(
                        client,
                        statuscodes.id_not_found,
                        details=f'No matches found: {message["id"]}',
                        listener=message["listener"]
                    )
                else:
                    send_statuscode(
                        client,
                        statuscodes.id_not_found,
                        details=f'No matches found: {message["id"]}'
                    )

                # End pmsg command handler
                return

            # Warn client if they are attempting to send to a username with multiple matches
            if self.warn_if_multiple_username_matches and len(tmp_client) >> 1:
                # Attach listener
                if "listener" in message:
                    send_statuscode(
                        client,
                        statuscodes.id_not_specific,
                        details=f'Multiple matches found for {message["id"]}, found {len(tmp_client)} matches. Please use Snowflakes or dict objects instead.',
                        listener=message["listener"]
                    )
                else:
                    send_statuscode(
                        client,
                        statuscodes.id_not_specific,
                        details=f'Multiple matches found for {message["id"]}, found {len(tmp_client)} matches. Please use Snowflakes or dict objects instead.'
                    )
                # End pmsg command handler
                return

            # Broadcast message to client
            tmp_message = {
                "cmd": "pmsg",
                "val": message["val"],
                "origin": {
                    "id": client.snowflake,
                    "username": client.username,
                    "uuid": str(client.id)
                }
            }
            server.send_packet(tmp_client, tmp_message)

            # Tell the origin client that the message sent successfully
            if "listener" in message:
                send_statuscode(
                    client,
                    statuscodes.ok,
                    listener=message["listener"]
                )
            else:
                send_statuscode(
                    client,
                    statuscodes.ok
                )

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
            # Require sending client to have set their username
            if not client.username_set:
                # Attach listener
                if "listener" in message:
                    send_statuscode(
                        client,
                        statuscodes.id_required,
                        details="This command requires setting a username.",
                        listener=message["listener"]
                    )
                else:
                    send_statuscode(
                        client,
                        statuscodes.id_required,
                        details="This command requires setting a username."
                    )

                # End pmsg command handler
                return

            tmp_client = None

            # Validate schema
            if not valid(client, message, self.protocol.pvar):
                return

            # Find client
            try:
                tmp_client = server.clients_manager.find_obj(message['id'])

            # No objects found
            except server.clients_manager.exceptions.NoResultsFound:

                # Attach listener
                if "listener" in message:
                    send_statuscode(
                        client,
                        statuscodes.id_not_found,
                        details=f'No matches found: {message["id"]}',
                        listener=message["listener"]
                    )
                else:
                    send_statuscode(
                        client,
                        statuscodes.id_not_found,
                        details=f'No matches found: {message["id"]}'
                    )

                # End pvar command handler
                return

            # Broadcast message to client
            tmp_message = {
                "cmd": "pvar",
                "name": message["name"],
                "val": message["val"],
                "origin": {
                    "id": client.snowflake,
                    "username": client.username,
                    "uuid": str(client.id)
                }
            }
            server.send_packet(client, tmp_message)

            # Tell the origin client that the message sent successfully
            if "listener" in message:
                send_statuscode(
                    client,
                    statuscodes.ok,
                    listener=message["listener"]
                )
            else:
                send_statuscode(
                    client,
                    statuscodes.ok
                )

        @server.on_command(cmd="setid", schema=self.protocol)
        async def on_setid(client, message):
            # Validate schema
            if not valid(client, message, self.protocol.setid):
                return

            # Prevent setting the username more than once
            if client.username_set:
                server.logger.error(f"Client {client.snowflake} attempted to set username again!")
                if "listener" in message:
                    send_statuscode(
                        client,
                        statuscodes.id_already_set,
                        val={
                            "id": client.snowflake,
                            "username": client.username
                        },
                        listener=message["listener"]
                    )
                else:
                    send_statuscode(
                        client,
                        statuscodes.id_already_set,
                        val={
                            "id": client.snowflake,
                            "username": client.username
                        }
                    )

                # Exit setid command
                return

            # Set the username
            server.clients_manager.set_username(client, message['val'])

            # Attach listener (if present) and broadcast
            if "listener" in message:
                send_statuscode(
                    client,
                    statuscodes.ok,
                    val={
                        "id": client.snowflake,
                        "username": client.username,
                        "uuid": str(client.id)
                    },
                    listener=message["listener"])
            else:
                send_statuscode(
                    client,
                    statuscodes.ok,
                    val={
                        "id": client.snowflake,
                        "username": client.username,
                        "uuid": str(client.id)
                    },
                )

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
            val = None
            listener = None

            if "val" in message:
                val = message["val"]

            if "listener" in message:
                listener = message["listener"]

            send_statuscode(client, statuscodes.echo, val=val, listener=listener)
