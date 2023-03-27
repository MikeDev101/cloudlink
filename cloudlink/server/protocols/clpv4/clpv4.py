from .schema import cl4_protocol

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

        # Exposes the schema of the protocol.
        self.schema = cl4_protocol

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

            @staticmethod
            def generate(code: tuple):
                return f"{code[0]}:{code[1]} | {code[2]}", code[1]

        # Expose statuscodes class for extension usage
        self.statuscodes = statuscodes

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

        # Expose get_client_ip for extension usage
        self.get_client_ip = get_client_ip

        # valid(message, schema): Used to verify messages.
        def valid(client, message, schema):
            if server.validator(message, schema):
                return True

            # Alert the client that the schema was invalid
            send_statuscode(client, statuscodes.syntax, details=dict(server.validator.errors))
            return False

        # Expose validator function for extension usage
        self.valid = valid

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

        # Expose the statuscode generator for extension usage
        self.send_statuscode = send_statuscode

        # Simplify alerting users that a command requires a username to be set
        def require_username_set(client, message):
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

            return client.username_set

        # Expose username requirement function for extension usage
        self.require_username_set = require_username_set

        # Tool for gathering client rooms
        def gather_rooms(client, message):
            if "rooms" in message:
                # Read value from message
                rooms = message["rooms"]

                # Convert to set
                if type(rooms) == str:
                    rooms = {rooms}
                if type(rooms) == list:
                    rooms = set(rooms)

                return rooms
            else:
                # Use all subscribed rooms
                return client.rooms

        # Expose rooms gatherer for extension usage
        self.gather_rooms = gather_rooms

        # Exception handlers

        @server.on_exception(exception_type=server.exceptions.ValidationError, schema=cl4_protocol)
        async def validation_failure(client, details):
            send_statuscode(client, statuscodes.syntax, details=dict(details))

        @server.on_exception(exception_type=server.exceptions.InvalidCommand, schema=cl4_protocol)
        async def invalid_command(client, details):
            send_statuscode(
                client,
                statuscodes.invalid_command,
                details=f"{details} is an invalid command."
            )

        @server.on_disabled_command(schema=cl4_protocol)
        async def disabled_command(client, details):
            send_statuscode(
                client,
                statuscodes.disabled_command,
                details=f"{details} is a disabled command."
            )

        @server.on_exception(exception_type=server.exceptions.JSONError, schema=cl4_protocol)
        async def json_exception(client, details):
            send_statuscode(
                client,
                statuscodes.json_error,
                details=f"A JSON error was raised: {details}"
            )

        @server.on_exception(exception_type=server.exceptions.EmptyMessage, schema=cl4_protocol)
        async def empty_message(client, details):
            send_statuscode(
                client,
                statuscodes.empty_packet,
                details="Your client has sent an empty message."
            )

        # Protocol identified event
        @server.on_protocol_identified(schema=cl4_protocol)
        async def protocol_identified(client):
            server.logger.debug(f"Adding client {client.snowflake} to default room.")
            server.rooms_manager.subscribe(client, "default")

        # The CLPv4 command set

        @server.on_command(cmd="handshake", schema=cl4_protocol)
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

            # Send userlists of any rooms
            async for room in server.async_iterable(client.rooms):
                server.send_packet(client, {
                    "cmd": "ulist",
                    "val": {
                        "mode": "set",
                        "val": server.rooms_manager.generate_userlist(room, cl4_protocol)
                    }
                })

            # Attach listener
            if "listener" in message:
                send_statuscode(client, statuscodes.ok, listener=message["listener"])
            else:
                send_statuscode(client, statuscodes.ok)

        @server.on_command(cmd="ping", schema=cl4_protocol)
        async def on_ping(client, message):
            if "listener" in message:
                send_statuscode(client, statuscodes.ok, listener=message["listener"])
            else:
                send_statuscode(client, statuscodes.ok)

        @server.on_command(cmd="gmsg", schema=cl4_protocol)
        async def on_gmsg(client, message):
            # Validate schema
            if not valid(client, message, cl4_protocol.gmsg):
                return

            # Gather rooms to send to
            rooms = gather_rooms(client, message)

            # Broadcast to all subscribed rooms
            async for room in server.async_iterable(rooms):

                # Prevent accessing rooms not joined
                if room not in client.rooms:

                    # Attach listener
                    if "listener" in message:
                        send_statuscode(
                            client,
                            statuscodes.room_not_joined,
                            details=f'Attempted to access room {room} while not joined.',
                            listener=message["listener"]
                        )
                    else:
                        send_statuscode(
                            client,
                            statuscodes.room_not_joined,
                            details=f'Attempted to access room {room} while not joined.'
                        )

                    # Stop gmsg command
                    return

                clients = await server.rooms_manager.get_all_in_rooms(room, cl4_protocol)

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
                        "listener": message["listener"],
                        "room": room
                    }

                    # Unicast message
                    server.send_packet(client, tmp_message)
                else:
                    # Define the message to broadcast
                    tmp_message = {
                        "cmd": "gmsg",
                        "val": message["val"],
                        "room": room
                    }

                    # Broadcast message
                    server.send_packet(clients, tmp_message)

        @server.on_command(cmd="pmsg", schema=cl4_protocol)
        async def on_pmsg(client, message):
            # Validate schema
            if not valid(client, message, cl4_protocol.pmsg):
                return

            # Require sending client to have set their username
            if not require_username_set(client, message):
                return

            # Gather rooms
            rooms = gather_rooms(client, message)

            # Search and send to all specified clients in rooms
            any_results_found = False
            async for room in server.async_iterable(rooms):

                # Prevent accessing rooms not joined
                if room not in client.rooms:

                    # Attach listener
                    if "listener" in message:
                        send_statuscode(
                            client,
                            statuscodes.room_not_joined,
                            details=f'Attempted to access room {room} while not joined.',
                            listener=message["listener"]
                        )
                    else:
                        send_statuscode(
                            client,
                            statuscodes.room_not_joined,
                            details=f'Attempted to access room {room} while not joined.'
                        )

                    # Stop pmsg command
                    return

                clients = await server.rooms_manager.get_specific_in_room(room, cl4_protocol, message['id'])

                # Continue if no results are found
                if not len(clients):
                    continue

                # Mark the full search OK
                if not any_results_found:
                    any_results_found = True

                # Warn if multiple matches are found (mainly for username queries)
                if self.warn_if_multiple_username_matches and len(clients) >> 1:
                    # Attach listener
                    if "listener" in message:
                        send_statuscode(
                            client,
                            statuscodes.id_not_specific,
                            details=f'Multiple matches found for {message["id"]}, found {len(clients)} matches. Please use Snowflakes, UUIDs, or client objects instead.',
                            listener=message["listener"]
                        )
                    else:
                        send_statuscode(
                            client,
                            statuscodes.id_not_specific,
                            details=f'Multiple matches found for {message["id"]}, found {len(clients)} matches. Please use Snowflakes, UUIDs, or client objects instead.'
                        )

                    # Stop pmsg command
                    return

                # Send message
                tmp_message = {
                    "cmd": "pmsg",
                    "val": message["val"],
                    "origin": {
                        "id": client.snowflake,
                        "username": client.username,
                        "uuid": str(client.id)
                    },
                    "room": room
                }
                server.send_packet(clients, tmp_message)

            if not any_results_found:
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

            # Results were found and sent successfully
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

        @server.on_command(cmd="gvar", schema=cl4_protocol)
        async def on_gvar(client, message):

            # Validate schema
            if not valid(client, message, cl4_protocol.gvar):
                return

            # Gather rooms to send to
            rooms = gather_rooms(client, message)

            # Broadcast to all subscribed rooms
            async for room in server.async_iterable(rooms):

                # Prevent accessing rooms not joined
                if room not in client.rooms:

                    # Attach listener
                    if "listener" in message:
                        send_statuscode(
                            client,
                            statuscodes.room_not_joined,
                            details=f'Attempted to access room {room} while not joined.',
                            listener=message["listener"]
                        )
                    else:
                        send_statuscode(
                            client,
                            statuscodes.room_not_joined,
                            details=f'Attempted to access room {room} while not joined.'
                        )

                    # Stop gvar command
                    return

                clients = await server.rooms_manager.get_all_in_rooms(room, cl4_protocol)

                # Define the message to send
                tmp_message = {
                    "cmd": "gvar",
                    "name": message["name"],
                    "val": message["val"],
                    "room": room
                }

                # Attach listener (if present) and broadcast
                if "listener" in message:
                    clients.remove(client)
                    server.send_packet(clients, tmp_message)
                    tmp_message["listener"] = message["listener"]
                    server.send_packet(client, tmp_message)
                else:
                    server.send_packet(clients, tmp_message)

        @server.on_command(cmd="pvar", schema=cl4_protocol)
        async def on_pvar(client, message):
            # Validate schema
            if not valid(client, message, cl4_protocol.pvar):
                return

            # Require sending client to have set their username
            if not require_username_set(client, message):
                return

            # Gather rooms
            rooms = gather_rooms(client, message)

            # Search and send to all specified clients in rooms
            any_results_found = False
            async for room in server.async_iterable(rooms):

                # Prevent accessing rooms not joined
                if room not in client.rooms:

                    # Attach listener
                    if "listener" in message:
                        send_statuscode(
                            client,
                            statuscodes.room_not_joined,
                            details=f'Attempted to access room {room} while not joined.',
                            listener=message["listener"]
                        )
                    else:
                        send_statuscode(
                            client,
                            statuscodes.room_not_joined,
                            details=f'Attempted to access room {room} while not joined.'
                        )

                    # Stop pvar command
                    return

                clients = await server.rooms_manager.get_specific_in_room(room, cl4_protocol, message['id'])

                # Continue if no results are found
                if not len(clients):
                    continue

                # Mark the full search OK
                if not any_results_found:
                    any_results_found = True

                # Warn if multiple matches are found (mainly for username queries)
                if self.warn_if_multiple_username_matches and len(clients) >> 1:
                    # Attach listener
                    if "listener" in message:
                        send_statuscode(
                            client,
                            statuscodes.id_not_specific,
                            details=f'Multiple matches found for {message["id"]}, found {len(clients)} matches. Please use Snowflakes, UUIDs, or client objects instead.',
                            listener=message["listener"]
                        )
                    else:
                        send_statuscode(
                            client,
                            statuscodes.id_not_specific,
                            details=f'Multiple matches found for {message["id"]}, found {len(clients)} matches. Please use Snowflakes, UUIDs, or client objects instead.'
                        )

                    # Stop pvar command
                    return

                # Send message
                tmp_message = {
                    "cmd": "pvar",
                    "name": message["name"],
                    "val": message["val"],
                    "origin": {
                        "id": client.snowflake,
                        "username": client.username,
                        "uuid": str(client.id)
                    },
                    "room": room
                }
                server.send_packet(clients, tmp_message)

            if not any_results_found:
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

            # Results were found and sent successfully
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

        @server.on_command(cmd="setid", schema=cl4_protocol)
        async def on_setid(client, message):
            # Validate schema
            if not valid(client, message, cl4_protocol.setid):
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
                            "username": client.username,
                            "uuid": str(client.id)
                        },
                        listener=message["listener"]
                    )
                else:
                    send_statuscode(
                        client,
                        statuscodes.id_already_set,
                        val={
                            "id": client.snowflake,
                            "username": client.username,
                            "uuid": str(client.id)
                        }
                    )

                # Exit setid command
                return

            # Gather rooms
            rooms = server.copy(client.rooms)

            # Leave all rooms
            async for room in server.async_iterable(rooms):
                server.rooms_manager.unsubscribe(client, room)

            # Set the username
            server.clients_manager.set_username(client, message['val'])

            # Re-join rooms
            async for room in server.async_iterable(rooms):
                server.rooms_manager.subscribe(client, room)

                # Broadcast userlist state
                clients = await server.rooms_manager.get_all_in_rooms(room, cl4_protocol)
                server.send_packet(clients, {
                    "cmd": "ulist",
                    "val": {
                        "mode": "add",
                        "val": server.clients_manager.generate_user_object(client)
                    }
                })

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

        @server.on_command(cmd="link", schema=cl4_protocol)
        async def on_link(client, message):
            # Validate schema
            if not valid(client, message, cl4_protocol.linking):
                return

            # Require sending client to have set their username
            if not require_username_set(client, message):
                return

            # Clear all rooms beforehand
            async for room in server.async_iterable(client.rooms):
                server.rooms_manager.unsubscribe(client, room)

            # Convert to set
            if type(message["val"]) in [list, str]:
                if type(message["val"]) == list:
                    message["val"] = set(message["val"])
                if type(message["val"]) == str:
                    message["val"] = {message["val"]}

            async for room in server.async_iterable(message["val"]):
                server.rooms_manager.subscribe(client, room)

        @server.on_command(cmd="unlink", schema=cl4_protocol)
        async def on_unlink(client, message):
            # Validate schema
            if not valid(client, message, cl4_protocol.linking):
                return

            # Require sending client to have set their username
            if not require_username_set(client, message):
                return

            # Convert to set
            if type(message["val"]) in [list, str]:
                if type(message["val"]) == list:
                    message["val"] = set(message["val"])
                if type(message["val"]) == str:
                    message["val"] = {message["val"]}

            async for room in server.async_iterable(message["val"]):
                server.rooms_manager.unsubscribe(client, room)

            # Re-link to default room if no rooms are joined
            if not len(client.rooms):
                server.rooms_manager.subscribe(client, "default")

        @server.on_command(cmd="direct", schema=cl4_protocol)
        async def on_direct(client, message):
            # Validate schema
            if not valid(client, message, cl4_protocol.direct):
                return

            try:
                client = server.clients_manager.find_obj(message["id"])

                tmp_msg = {
                    "cmd": "direct",
                    "val": message["val"]
                }

                if client.username_set:
                    tmp_msg["origin"] = {
                        "id": client.snowflake,
                        "username": client.username,
                        "uuid": str(client.id)
                    }

                else:
                    tmp_msg["origin"] = {
                        "id": client.snowflake,
                        "uuid": str(client.id)
                    }

                if "listener" in message:
                    tmp_msg["listener"] = message["listener"]

                server.send_packet_unicast(client, tmp_msg)

            except server.clients_manager.exceptions.NoResultsFound:
                # Attach listener
                if "listener" in message:
                    send_statuscode(
                        client,
                        statuscodes.id_not_found,
                        listener=message["listener"]
                    )
                else:
                    send_statuscode(
                        client,
                        statuscodes.id_not_found
                    )

                # Stop direct command
                return

        @server.on_command(cmd="bridge", schema=cl4_protocol)
        async def on_bridge(client, message):
            pass
