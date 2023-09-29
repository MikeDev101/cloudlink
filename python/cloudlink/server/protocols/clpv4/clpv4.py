from .schema import cl4_protocol

"""
This is the default protocol used for the CloudLink server.
The CloudLink 4.1 Protocol retains full support for CLPv4.

Each packet format is compliant with UPLv2 formatting rules.

Documentation for the CLPv4.1 protocol can be found here:
https://github.com/MikeDev101/cloudlink/wiki/The-CloudLink-Protocol
"""


class clpv4:
    def __init__(self, server):

        """
        Configuration settings

        warn_if_multiple_username_matches: Boolean, Default: True
        If True, the server will warn users if they are resolving multiple clients for a username search.

        enable_motd: Boolean, Default: False
        If True, whenever a client sends the handshake command or whenever the client's protocol is identified,
        the server will send the Message-Of-The-Day from whatever value motd_message is set to.

        motd_message: String, Default: Blank string
        If enable_mod is True, this string will be sent as the server's Message-Of-The-Day.

        real_ip_header: String, Default: None
        If you use CloudLink behind a tunneling service or reverse proxy, set this value to whatever
        IP address-fetching request header to resolve valid IP addresses. When set to None, it will
        utilize the host's incoming network for resolving IP addresses.

        Examples include:
        * x-forwarded-for
        * cf-connecting-ip

        """
        self.warn_if_multiple_username_matches = True
        self.enable_motd = False
        self.motd_message = str()
        self.real_ip_header = None

        # Exposes the schema of the protocol.
        self.schema = cl4_protocol
        self.__qualname__ = "clpv4"

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
            # Grab IP address using headers
            if self.real_ip_header:
                if self.real_ip_header in client.request_headers:
                    return client.request_headers.get(self.real_ip_header)

            # Use system identified IP address
            if type(client.remote_address) == tuple:
                return str(client.remote_address[0])

        # Expose get_client_ip for extension usage
        self.get_client_ip = get_client_ip

        # valid(message, schema): Used to verify messages.
        def valid(client, message, schema, allow_unknown=True):
        
            validator = server.validator(schema, allow_unknown=allow_unknown)
            
            if validator.validate(message):
                return True

            # Alert the client that the schema was invalid
            send_statuscode(client, statuscodes.syntax, details=dict(validator.errors))
            return False

        # Expose validator function for extension usage
        self.valid = valid

        # Simplify sending error/info messages
        def send_statuscode(client, code, details=None, message=None, val=None):
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

            if message:
                if "listener" in message:
                    tmp_message["listener"] = message["listener"]

            if val:
                tmp_message["val"] = val

            # Send the code
            server.send_packet(client, tmp_message)

        # Expose the statuscode generator for extension usage
        self.send_statuscode = send_statuscode

        # Send messages with automatic listener attaching
        def send_message(client, payload, message=None):
            if message:
                if "listener" in message:
                    payload["listener"] = message["listener"]

            # Send the code
            server.send_packet(client, payload)

        # Expose the message sender for extension usage
        self.send_message = send_message

        # Simplify alerting users that a command requires a username to be set
        def require_username_set(client, message):
            if not client.username_set:
                send_statuscode(
                    client,
                    statuscodes.id_required,
                    details="This command requires setting a username.",
                    message=message
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

        # Generate a user object
        def generate_user_object(obj):
            # Username set
            if obj.username_set:
                return {
                    "id": obj.snowflake,
                    "username": obj.username,
                    "uuid": str(obj.id)
                }

            # Username not set
            return {
                "id": obj.snowflake,
                "uuid": str(obj.id)
            }

        # Expose username object generator function for extension usage
        self.generate_user_object = generate_user_object

        # If the client has not explicitly used the handshake command, send them the handshake data
        async def notify_handshake(client):
            # Don't execute this if handshake was already done
            if client.handshake:
                return
            client.handshake = True

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
                "cmd": "client_obj",
                "val": generate_user_object(client)
            })

            # Send userlists of rooms
            async for room in server.async_iterable(client.rooms):
                server.send_packet(client, {
                    "cmd": "ulist",
                    "mode": "set",
                    "val": server.rooms_manager.generate_userlist(room, cl4_protocol),
                    "rooms": room
                })

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
        async def empty_message(client):
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

        @server.on_protocol_disconnect(schema=cl4_protocol)
        async def protocol_disconnect(client):
            server.logger.debug(f"Removing client {client.snowflake} from rooms...")

            # Unsubscribe from all rooms
            async for room_id in server.async_iterable(server.copy(client.rooms)):
                server.rooms_manager.unsubscribe(client, room_id)

                # Don't bother with notifying if client username wasn't set
                if not client.username_set:
                    continue

                # Notify rooms of removed client
                clients = await server.rooms_manager.get_all_in_rooms(room_id, cl4_protocol)
                clients = server.copy(clients)
                server.send_packet(clients, {
                    "cmd": "ulist",
                    "mode": "remove",
                    "val": generate_user_object(client),
                    "rooms": room_id
                })

        # The CLPv4 command set

        @server.on_command(cmd="handshake", schema=cl4_protocol)
        async def on_handshake(client, message):
            await notify_handshake(client)
            send_statuscode(client, statuscodes.ok, message=message)

        @server.on_command(cmd="ping", schema=cl4_protocol)
        async def on_ping(client, message):
            send_statuscode(client, statuscodes.ok, message=message)

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
                    send_statuscode(
                        client,
                        statuscodes.room_not_joined,
                        details=f'Attempted to access room {room} while not joined.',
                        message=message
                    )

                    # Stop gmsg command
                    return

                clients = await server.rooms_manager.get_all_in_rooms(room, cl4_protocol)
                clients = server.copy(clients)

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
                        "rooms": room
                    }

                    # Unicast message
                    server.send_packet(client, tmp_message)
                else:
                    # Broadcast message
                    server.send_packet(clients, {
                        "cmd": "gmsg",
                        "val": message["val"],
                        "rooms": room
                    })

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
                    send_statuscode(
                        client,
                        statuscodes.room_not_joined,
                        details=f'Attempted to access room {room} while not joined.',
                        message=message
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
                    send_statuscode(
                        client,
                        statuscodes.id_not_specific,
                        details=f'Multiple matches found for {message["id"]}, found {len(clients)} matches. Please use Snowflakes, UUIDs, or client objects instead.',
                        message=message
                    )

                    # Stop pmsg command
                    return

                # Send message
                tmp_message = {
                    "cmd": "pmsg",
                    "val": message["val"],
                    "origin": generate_user_object(client),
                    "rooms": room
                }
                server.send_packet(clients, tmp_message)

            if not any_results_found:
                send_statuscode(
                    client,
                    statuscodes.id_not_found,
                    details=f'No matches found: {message["id"]}',
                    message=message
                )

                # End pmsg command handler
                return

            # Results were found and sent successfully
            send_statuscode(
                client,
                statuscodes.ok,
                message=message
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
                    send_statuscode(
                        client,
                        statuscodes.room_not_joined,
                        details=f'Attempted to access room {room} while not joined.',
                        message=message
                    )

                    # Stop gvar command
                    return

                clients = await server.rooms_manager.get_all_in_rooms(room, cl4_protocol)
                clients = server.copy(clients)

                # Define the message to send
                tmp_message = {
                    "cmd": "gvar",
                    "name": message["name"],
                    "val": message["val"],
                    "rooms": room
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
                    send_statuscode(
                        client,
                        statuscodes.room_not_joined,
                        details=f'Attempted to access room {room} while not joined.',
                        message=message
                    )

                    # Stop pvar command
                    return

                clients = await server.rooms_manager.get_specific_in_room(room, cl4_protocol, message['id'])
                clients = server.copy(clients)

                # Continue if no results are found
                if not len(clients):
                    continue

                # Mark the full search OK
                if not any_results_found:
                    any_results_found = True

                # Warn if multiple matches are found (mainly for username queries)
                if self.warn_if_multiple_username_matches and len(clients) >> 1:
                    send_statuscode(
                        client,
                        statuscodes.id_not_specific,
                        details=f'Multiple matches found for {message["id"]}, found {len(clients)} matches. Please use Snowflakes, UUIDs, or client objects instead.',
                        message=message
                    )

                    # Stop pvar command
                    return

                # Send message
                tmp_message = {
                    "cmd": "pvar",
                    "name": message["name"],
                    "val": message["val"],
                    "origin": generate_user_object(client),
                    "rooms": room
                }
                server.send_packet(clients, tmp_message)

            if not any_results_found:
                send_statuscode(
                    client,
                    statuscodes.id_not_found,
                    details=f'No matches found: {message["id"]}',
                    message=message
                )

                # End pmsg command handler
                return

            # Results were found and sent successfully
            send_statuscode(
                client,
                statuscodes.ok,
                message=message
            )

        @server.on_command(cmd="setid", schema=cl4_protocol)
        async def on_setid(client, message):
            # Validate schema
            if not valid(client, message, cl4_protocol.setid):
                return

            # Prevent setting the username more than once
            if client.username_set:
                server.logger.error(f"Client {client.snowflake} attempted to set username again!")
                send_statuscode(
                    client,
                    statuscodes.id_already_set,
                    val=generate_user_object(client),
                    message=message
                )

                # Exit setid command
                return

            # Leave default room
            server.rooms_manager.unsubscribe(client, "default")

            # Set the username
            server.clients_manager.set_username(client, message['val'])

            # Re-join default room
            server.rooms_manager.subscribe(client, "default")

            # Broadcast userlist state to existing members
            clients = await server.rooms_manager.get_all_in_rooms("default", cl4_protocol)
            clients = server.copy(clients)
            clients.remove(client)
            server.send_packet(clients, {
                "cmd": "ulist",
                "mode": "add",
                "val": generate_user_object(client),
                "rooms": "default"
            })

            # Notify client of current room state
            server.send_packet(client, {
                "cmd": "ulist",
                "mode": "set",
                "val": server.rooms_manager.generate_userlist("default", cl4_protocol),
                "rooms": "default"
            })

            # Attach listener (if present) and broadcast
            send_statuscode(
                client,
                statuscodes.ok,
                val=generate_user_object(client),
                message=message
            )

        @server.on_command(cmd="link", schema=cl4_protocol)
        async def on_link(client, message):
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
            
            # Unsubscribe from default room if not mentioned
            if not "default" in message["val"]:
                server.rooms_manager.unsubscribe(client, "default")
                
                # Broadcast userlist state to existing members
                clients = await server.rooms_manager.get_all_in_rooms("default", cl4_protocol)
                clients = server.copy(clients)
                server.send_packet(clients, {
                    "cmd": "ulist",
                    "mode": "remove",
                    "val": generate_user_object(client),
                    "rooms": "default"
                })

            async for room in server.async_iterable(message["val"]):
                server.rooms_manager.subscribe(client, room)

                # Broadcast userlist state to existing members
                clients = await server.rooms_manager.get_all_in_rooms(room, cl4_protocol)
                clients = server.copy(clients)
                clients.remove(client)
                server.send_packet(clients, {
                    "cmd": "ulist",
                    "mode": "add",
                    "val": generate_user_object(client),
                    "rooms": room
                })

                # Notify client of current room state
                server.send_packet(client, {
                    "cmd": "ulist",
                    "mode": "set",
                    "val": server.rooms_manager.generate_userlist(room, cl4_protocol),
                    "rooms": room
                })

            # Attach listener (if present) and broadcast
            send_statuscode(
                client,
                statuscodes.ok,
                message=message
            )

        @server.on_command(cmd="unlink", schema=cl4_protocol)
        async def on_unlink(client, message):
            # Validate schema
            if not valid(client, message, cl4_protocol.linking):
                return

            # Require sending client to have set their username
            if not require_username_set(client, message):
                return

            # If blank, assume all rooms
            if type(message["val"]) == str and not len(message["val"]):
                message["val"] = client.rooms

            # Convert to set
            if type(message["val"]) in [list, str]:
                if type(message["val"]) == list:
                    message["val"] = set(message["val"])
                if type(message["val"]) == str:
                    message["val"] = {message["val"]}

            async for room in server.async_iterable(message["val"]):
                server.rooms_manager.unsubscribe(client, room)

                # Broadcast userlist state to existing members
                clients = await server.rooms_manager.get_all_in_rooms(room, cl4_protocol)
                clients = server.copy(clients)
                server.send_packet(clients, {
                    "cmd": "ulist",
                    "mode": "remove",
                    "val": generate_user_object(client),
                    "rooms": room
                })

            # Re-link to default room if no rooms are joined
            if not len(client.rooms):
                server.rooms_manager.subscribe(client, "default")

                # Broadcast userlist state to existing members
                clients = await server.rooms_manager.get_all_in_rooms("default", cl4_protocol)
                clients = server.copy(clients)
                clients.remove(client)
                server.send_packet(clients, {
                    "cmd": "ulist",
                    "mode": "add",
                    "val": generate_user_object(client),
                    "rooms": "default"
                })

                # Notify client of current room state
                server.send_packet(client, {
                    "cmd": "ulist",
                    "mode": "set",
                    "val": server.rooms_manager.generate_userlist("default", cl4_protocol),
                    "rooms": "default"
                })

            # Attach listener (if present) and broadcast
            send_statuscode(
                client,
                statuscodes.ok,
                message=message
            )

        @server.on_command(cmd="direct", schema=cl4_protocol)
        async def on_direct(client, message):
            # Validate schema
            if not valid(client, message, cl4_protocol.direct):
                return

            try:
                tmp_client = server.clients_manager.find_obj(message["id"])

                tmp_msg = {
                    "cmd": "direct",
                    "val": message["val"]
                }

                if client.username_set:
                    tmp_msg["origin"] = generate_user_object(client)

                else:
                    tmp_msg["origin"] = {
                        "id": client.snowflake,
                        "uuid": str(client.id)
                    }

                if "listener" in message:
                    tmp_msg["listener"] = message["listener"]

                server.send_packet_unicast(tmp_client, tmp_msg)

            except server.clients_manager.exceptions.NoResultsFound:
                send_statuscode(
                    client,
                    statuscodes.id_not_found,
                    message=message
                )

                # Stop direct command
                return
