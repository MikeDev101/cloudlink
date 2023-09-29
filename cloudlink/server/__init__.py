# Core components of the CloudLink server
import asyncio
import cerberus
import logging
import time
from copy import copy
from snowflake import SnowflakeGenerator

# Import websockets and SSL support
import websockets
import ssl

# Import shared modules
from ..async_iterables import async_iterable

# Import server-specific modules
from .modules.clients_manager import clients_manager
from .modules.rooms_manager import rooms_manager

# Import JSON library - Prefer UltraJSON but use native JSON if failed
try:
    import ujson
except Exception as e:
    print(f"Server failed to import UltraJSON, failing back to native JSON library. Exception code: {e}")
    import json as ujson


# Define server exceptions
class exceptions:
    class EmptyMessage(Exception):
        """This exception is raised when a client sends an empty packet."""
        pass

    class InvalidCommand(Exception):
        """This exception is raised when a client sends an invalid command for it's determined protocol."""
        pass

    class JSONError(Exception):
        """This exception is raised when the server fails to parse a message's JSON."""
        pass

    class ValidationError(Exception):
        """This exception is raised when a client with a known protocol sends a message that fails validation before commands can execute."""
        pass

    class InternalError(Exception):
        """This exception is raised when an unexpected and/or unhandled exception is raised."""
        pass

    class Overloaded(Exception):
        """This exception is raised when the server believes it is overloaded."""
        pass


# Main server
class server:
    def __init__(self):
        self.version = "0.2.0"

        # Logging
        self.logging = logging
        self.logger = self.logging.getLogger(__name__)

        # Asyncio
        self.asyncio = asyncio

        # Configure websocket framework
        self.ws = websockets

        # Components
        self.ujson = ujson
        self.gen = SnowflakeGenerator(42)
        self.validator = cerberus.Validator
        self.async_iterable = async_iterable
        self.copy = copy
        self.clients_manager = clients_manager(self)
        self.rooms_manager = rooms_manager(self)
        self.exceptions = exceptions()

        # Dictionary containing protocols as keys and sets of commands as values
        self.disabled_commands = dict()

        # Create event managers
        self.on_connect_events = set()
        self.on_message_events = set()
        self.on_disconnect_events = set()
        self.on_error_events = set()
        self.exception_handlers = dict()
        self.disabled_commands_handlers = dict()
        self.protocol_identified_events = dict()
        self.protocol_disconnect_events = dict()

        # Create method handlers
        self.command_handlers = dict()

        # Configure framework logging
        self.suppress_websocket_logs = True

        # Set to -1 to allow as many client as possible
        self.max_clients = -1

        # Configure SSL support
        self.ssl_enabled = False
        self.ssl_context = None

    # Enables SSL support
    def enable_ssl(self, certfile, keyfile):
        try:
            self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            self.ssl_context.load_cert_chain(certfile=certfile, keyfile=keyfile)
            self.ssl_enabled = True
            self.logger.info(f"SSL support initialized!")
        except Exception as e:
            self.logger.error(f"Failed to initialize SSL support! {e}")

    # Runs the server.
    def run(self, ip="127.0.0.1", port=3000):
        try:
            # Validate config before startup
            if type(self.max_clients) != int:
                raise TypeError(
                    "The max_clients value must be a integer value set to -1 (unlimited clients) or greater than zero!"
                )

            if self.max_clients < -1 or self.max_clients == 0:
                raise ValueError(
                    "The max_clients value must be a integer value set to -1 (unlimited clients) or greater than zero!"
                )

            # Startup message
            self.logger.info(f"CloudLink {self.version} - Now listening to {ip}:{port}")

            # Suppress websocket library logging
            if self.suppress_websocket_logs:
                self.logging.getLogger('asyncio').setLevel(self.logging.ERROR)
                self.logging.getLogger('asyncio.coroutines').setLevel(self.logging.ERROR)
                self.logging.getLogger('websockets.server').setLevel(self.logging.ERROR)
                self.logging.getLogger('websockets.protocol').setLevel(self.logging.ERROR)

            # Start server
            self.asyncio.run(self.__run__(ip, port))

        except KeyboardInterrupt:
            pass
    
    def unbind_command(self, cmd, schema):
        if schema not in self.command_handlers:
            raise ValueError
        if cmd not in self.command_handlers[schema]:
            raise ValueError
        self.logger.debug(f"Unbinding command {cmd} from {schema.__qualname__} command event manager")
        self.command_handlers[schema].pop(cmd)
    
    # Event binder for on_command events
    def on_command(self, cmd, schema):

        def bind_event(func):
            self.bind_callback(cmd, schema, func)

        # End on_command binder
        return bind_event

    # Event binder for on_error events with specific shemas/exception types
    def on_exception(self, exception_type, schema):
        def bind_event(func):

            # Create schema category for error event manager
            if schema not in self.exception_handlers:
                self.logger.debug(f"Creating protocol {schema.__qualname__} exception event manager")
                self.exception_handlers[schema] = dict()

            # Create error event handler
            if exception_type not in self.exception_handlers[schema]:
                self.exception_handlers[schema][exception_type] = set()

            # Add function to the error command handler
            self.logger.debug(f"Binding function {func.__name__} to exception {exception_type.__name__} in {schema.__qualname__} exception event manager")
            self.exception_handlers[schema][exception_type].add(func)

        # End on_error_specific binder
        return bind_event

    # Event binder for invalid command events with specific shemas/exception types
    def on_disabled_command(self, schema):
        def bind_event(func):
            # Create disabled command event manager
            if schema not in self.disabled_commands_handlers:
                self.logger.debug(f"Creating disabled command event manager {schema.__qualname__}")
                self.disabled_commands_handlers[schema] = set()

            # Add function to the error command handler
            self.logger.debug(f"Binding function {func.__name__} to {schema.__qualname__} disabled command event manager")
            self.disabled_commands_handlers[schema].add(func)

        # End on_error_specific binder
        return bind_event

    def on_protocol_identified(self, schema):
        def bind_event(func):
            # Create protocol identified event manager
            if schema not in self.protocol_identified_events:
                self.logger.debug(f"Creating protocol identified event manager {schema.__qualname__}")
                self.protocol_identified_events[schema] = set()

            # Add function to the protocol identified event manager
            self.logger.debug(f"Binding function {func.__name__} to {schema.__qualname__} protocol identified event manager")
            self.protocol_identified_events[schema].add(func)

        # End on_protocol_identified binder
        return bind_event

    def on_protocol_disconnect(self, schema):
        def bind_event(func):
            # Create protocol disconnect event manager
            if schema not in self.protocol_disconnect_events:
                self.logger.debug(f"Creating protocol disconnect event manager {schema.__qualname__}")
                self.protocol_disconnect_events[schema] = set()

            # Add function to the protocol disconnect event manager
            self.logger.debug(f"Binding function {func.__name__} to {schema.__qualname__} protocol disconnected event manager")
            self.protocol_disconnect_events[schema].add(func)

        # End on_protocol_disconnect binder
        return bind_event

    # Event binder for on_message events
    def on_message(self, func):
        self.logger.debug(f"Binding function {func.__name__} to on_message events")
        self.on_message_events.add(func)

    # Event binder for on_connect events.
    def on_connect(self, func):
        self.logger.debug(f"Binding function {func.__name__} to on_connect events")
        self.on_connect_events.add(func)

    # Event binder for on_disconnect events.
    def on_disconnect(self, func):
        self.logger.debug(f"Binding function {func.__name__} to on_disconnect events")
        self.on_disconnect_events.add(func)

    # Event binder for on_error events.
    def on_error(self, func):
        self.logger.debug(f"Binding function {func.__name__} to on_error events")
        self.on_error_events.add(func)

    # Friendly version of send_packet_unicast / send_packet_multicast
    def send_packet(self, obj, message):
        if type(obj) in [list, set]:
            self.asyncio.create_task(self.execute_multicast(obj, message))
        else:
            self.asyncio.create_task(self.execute_unicast(obj, message))

    # Send message to a single client
    def send_packet_unicast(self, client, message):
        # Create unicast task
        self.asyncio.create_task(self.execute_unicast(client, message))

    # Send message to multiple clients
    def send_packet_multicast(self, clients, message):
        # Create multicast task
        self.asyncio.create_task(self.execute_multicast(clients, message))

    # Close the connection to client(s)
    def close_connection(self, obj, code=1000, reason=""):
        if type(obj) in [list, set]:
            self.asyncio.create_task(self.execute_close_multi(obj, code, reason))
        else:
            self.asyncio.create_task(self.execute_close_single(obj, code, reason))

    # Command disabler
    def disable_command(self, cmd, schema):
        # Check if the schema has no disabled commands
        if schema not in self.disabled_commands:
            self.disabled_commands[schema] = set()

        # Check if the command isn't already disabled
        if cmd in self.disabled_commands[schema]:
            raise ValueError(
                f"The command {cmd} is already disabled in protocol {schema.__qualname__}, or was enabled beforehand.")

        # Disable the command
        self.disabled_commands[schema].add(cmd)
        self.logger.debug(f"Disabled command {cmd} in protocol {schema.__qualname__}")

    # Command enabler
    def enable_command(self, cmd, schema):
        # Check if the schema has disabled commands
        if schema not in self.disabled_commands:
            raise ValueError(f"There are no commands to disable in protocol {schema.__qualname__}.")

        # Check if the command is disabled
        if cmd not in self.disabled_commands[schema]:
            raise ValueError(
                f"The command {cmd} is already enabled in protocol {schema.__qualname__}, or wasn't disabled beforehand.")

        # Enable the command
        self.disabled_commands[schema].remove(cmd)
        self.logger.debug(f"Enabled command {cmd} in protocol {schema.__qualname__}")

        # Free up unused disablers
        if not len(self.disabled_commands[schema]):
            self.disabled_commands.pop(schema)

    # Message processor
    async def message_processor(self, client, message):

        # Empty packet
        if not len(message):
            self.logger.debug(f"Client {client.snowflake} sent empty message ")

            # Fire on_error events
            asyncio.create_task(self.execute_on_error_events(client, self.exceptions.EmptyMessage))

            # Fire exception handling events
            if client.protocol_set:
                self.asyncio.create_task(
                    self.execute_exception_handlers(
                        client=client,
                        exception_type=self.exceptions.EmptyMessage,
                        schema=client.protocol,
                        details="Empty message"
                    )
                )
            else:
                # Close the connection
                self.send_packet(client, "Empty message")
                self.close_connection(client, reason="Empty message")

            # End message_processor coroutine
            return

        # Parse JSON in message and convert to dict
        try:
            message = self.ujson.loads(message)

        except Exception as error:
            self.logger.debug(f"Client {client.snowflake} sent invalid JSON: {error}")

            # Fire on_error events
            self.asyncio.create_task(self.execute_on_error_events(client, error))

            # Fire exception handling events
            if client.protocol_set:
                self.asyncio.create_task(
                    self.execute_exception_handlers(
                        client=client,
                        exception_type=self.exceptions.JSONError,
                        schema=client.protocol,
                        details=error
                    )
                )

            else:
                # Close the connection
                self.send_packet(client, "Invalid JSON")
                self.close_connection(client, reason="Invalid JSON")

            # End message_processor coroutine
            return

        # Begin validation
        valid = False
        selected_protocol = None

        # Client protocol is unknown
        if not client.protocol:
            self.logger.debug(f"Trying to identify client {client.snowflake}'s protocol")

            # Identify protocol
            errorlist = list()
            
            for schema in self.command_handlers:
                validator = self.validator(schema.default, allow_unknown=True)
                if validator.validate(message):
                    valid = True
                    selected_protocol = schema
                    break
                else:
                    errorlist.append(validator.errors)

            if not valid:
                # Log failed identification
                self.logger.debug(f"Could not identify protocol used by client {client.snowflake}: {errorlist}")

                # Fire on_error events
                self.asyncio.create_task(self.execute_on_error_events(client, "Unable to identify protocol"))

                # Close the connection
                self.send_packet(client, "Unable to identify protocol")
                self.close_connection(client, reason="Unable to identify protocol")

                # End message_processor coroutine
                return

            # Log known protocol
            self.logger.debug(f"Client {client.snowflake} is using protocol {selected_protocol.__qualname__}")

            # Make the client's protocol known
            self.clients_manager.set_protocol(client, selected_protocol)

            # Fire protocol identified events
            self.asyncio.create_task(self.execute_protocol_identified_events(client, selected_protocol))

        else:
            self.logger.debug(
                f"Validating message from {client.snowflake} using protocol {client.protocol.__qualname__}")

            # Validate message using known protocol
            selected_protocol = client.protocol
            
            validator = self.validator(selected_protocol.default, allow_unknown=True)
            
            
            if not validator.validate(message):
                errors = validator.errors

                # Log failed validation
                self.logger.debug(f"Client {client.snowflake} sent message that failed validation: {errors}")

                # Fire on_error events
                self.asyncio.create_task(self.execute_on_error_events(client, errors))

                # Fire exception handling events
                if client.protocol_set:
                    self.asyncio.create_task(
                        self.execute_exception_handlers(
                            client=client,
                            exception_type=self.exceptions.ValidationError,
                            schema=client.protocol,
                            details=errors
                        )
                    )

                # End message_processor coroutine
                return

        # Check if command exists
        if message[selected_protocol.command_key] not in self.command_handlers[selected_protocol]:

            # Log invalid command
            self.logger.debug(
                f"Client {client.snowflake} sent an invalid command \"{message[selected_protocol.command_key]}\" in protocol {selected_protocol.__qualname__}")

            # Fire on_error events
            self.asyncio.create_task(self.execute_on_error_events(client, "Invalid command"))

            # Fire exception handling events
            if client.protocol_set:
                self.asyncio.create_task(
                    self.execute_exception_handlers(
                        client=client,
                        exception_type=self.exceptions.InvalidCommand,
                        schema=client.protocol,
                        details=message[selected_protocol.command_key]
                    )
                )

            # End message_processor coroutine
            return

        # Check if the command is disabled
        if selected_protocol in self.disabled_commands:
            if message[selected_protocol.command_key] in self.disabled_commands[selected_protocol]:
                self.logger.debug(
                    f"Client {client.snowflake} sent a disabled command \"{message[selected_protocol.command_key]}\" in protocol {selected_protocol.__qualname__}")

                # Fire disabled command event
                self.asyncio.create_task(
                    self.execute_disabled_command_events(
                        client,
                        selected_protocol,
                        message[selected_protocol.command_key]
                    )
                )

                # End message_processor coroutine
                return

        # Fire on_command events
        self.asyncio.create_task(
            self.execute_on_command_events(
                client,
                message,
                selected_protocol
            )
        )

        # Fire on_message events
        self.asyncio.create_task(
            self.execute_on_message_events(
                client,
                message
            )
        )

    # Connection handler
    async def connection_handler(self, client):

        # Limit the amount of clients connected
        if self.max_clients != -1:
            if len(self.clients_manager) >= self.max_clients:
                self.logger.warning("Server full: Refused a new connection")
                self.send_packet(client, "Server is full!")
                self.close_connection(client, reason="Server is full!")
                return

        # Startup client attributes
        client.snowflake = str(next(self.gen))
        client.protocol = None
        client.protocol_set = False
        client.rooms = set()
        client.username_set = False
        client.username = str()
        client.handshake = False

        # Begin tracking the lifetime of the client
        client.birth_time = time.monotonic()

        # Add to clients manager
        self.clients_manager.add(client)

        # Fire on_connect events
        self.asyncio.create_task(self.execute_on_connect_events(client))

        self.logger.debug(f"Client {client.snowflake} connected")

        # Run connection loop
        await self.connection_loop(client)

        # Remove from clients manager
        self.clients_manager.remove(client)

        # Fire on_disconnect events
        self.asyncio.create_task(self.execute_on_disconnect_events(client))

        # Execute all protocol-specific disconnect events
        if client.protocol_set:
            self.asyncio.create_task(
                self.execute_protocol_disconnect_events(client, client.protocol)
            )

        self.logger.debug(
            f"Client {client.snowflake} disconnected: Total lifespan of {time.monotonic() - client.birth_time} seconds.")

    # Connection loop - Redefine for use with another outside library
    async def connection_loop(self, client):
        # Primary asyncio loop for the lifespan of the websocket connection
        try:
            async for message in client:
                # Start keeping track of processing time
                start = time.perf_counter()
                self.logger.debug(f"Now processing message from client {client.snowflake}...")

                # Process the message
                await self.message_processor(client, message)

                # Log processing time
                self.logger.debug(
                    f"Done processing message from client {client.snowflake}. Processing took {time.perf_counter() - start} seconds.")

        # Handle unexpected disconnects
        except self.ws.exceptions.ConnectionClosedError:
            pass

        # Handle OK disconnects
        except self.ws.exceptions.ConnectionClosedOK:
            pass

        # Catch any unexpected exceptions
        except Exception as e:
            self.logger.critical(f"Unexpected exception was raised: {e}")

            # Fire on_error events
            self.asyncio.create_task(self.execute_on_error_events(client, f"Unexpected exception was raised: {e}"))

            # Fire exception handling events
            if client.protocol_set:
                self.asyncio.create_task(
                    self.execute_exception_handlers(
                        client=client,
                        exception_type=self.exceptions.InternalError,
                        schema=client.protocol,
                        details=f"Unexpected exception was raised: {e}"
                    )
                )

    # WebSocket-specific server loop
    async def __run__(self, ip, port):
        if self.ssl_enabled:
            # Run with SSL support
            async with self.ws.serve(self.connection_handler, ip, port, ssl=self.ssl_context):
                await self.asyncio.Future()
        else:
            # Run without SSL support
            async with self.ws.serve(self.connection_handler, ip, port):
                await self.asyncio.Future()

    # Asyncio event-handling coroutines

    async def execute_on_disconnect_events(self, client):
        events = [event(client) for event in self.on_disconnect_events]
        group = self.asyncio.gather(*events)
        await group

    async def execute_on_connect_events(self, client):
        events = [event(client) for event in self.on_connect_events]
        group = self.asyncio.gather(*events)
        await group

    async def execute_on_message_events(self, client, message):
        events = [event(client, message) for event in self.on_message_events]
        group = self.asyncio.gather(*events)
        await group

    async def execute_on_command_events(self, client, message, schema):
        events = [event(client, message) for event in self.command_handlers[schema][message[schema.command_key]]]
        group = self.asyncio.gather(*events)
        await group

    async def execute_on_error_events(self, client, errors):
        events = [event(client, errors) for event in self.on_error_events]
        group = self.asyncio.gather(*events)
        await group

    async def execute_exception_handlers(self, client, exception_type, schema, details):
        # Guard clauses
        if schema not in self.exception_handlers:
            return
        if exception_type not in self.exception_handlers[schema]:
            return

        # Fire events
        events = [event(client, details) for event in self.exception_handlers[schema][exception_type]]
        group = self.asyncio.gather(*events)
        await group

    async def execute_disabled_command_events(self, client, schema, cmd):
        # Guard clauses
        if schema not in self.disabled_commands_handlers:
            return

        # Fire events
        events = [event(client, cmd) for event in self.disabled_commands_handlers[schema]]
        group = self.asyncio.gather(*events)
        await group

    async def execute_protocol_identified_events(self, client, schema):
        # Guard clauses
        if schema not in self.protocol_identified_events:
            return

        # Fire events
        events = [event(client) for event in self.protocol_identified_events[schema]]
        group = self.asyncio.gather(*events)
        await group

    async def execute_protocol_disconnect_events(self, client, schema):
        # Guard clauses
        if schema not in self.protocol_disconnect_events:
            return

        # Fire events
        events = [event(client) for event in self.protocol_disconnect_events[schema]]
        group = self.asyncio.gather(*events)
        await group

    # WebSocket-specific coroutines

    async def execute_unicast(self, client, message):
        # Guard clause
        if type(message) not in [dict, str]:
            raise TypeError(f"Supported datatypes for messages are dicts and strings, got type {type(message)}.")

        # Convert dict to JSON
        if type(message) == dict:
            message = self.ujson.dumps(message)

        # Attempt to send the packet
        try:
            await client.send(message)
        except Exception as e:
            self.logger.critical(
                f"Unexpected exception was raised while sending message to client {client.snowflake}: {e}"
            )

    async def execute_multicast(self, clients, message):
        # Multicast the message
        events = [self.execute_unicast(client, message) for client in clients]
        group = self.asyncio.gather(*events)
        await group

    async def execute_close_single(self, client, code=1000, reason=""):
        try:
            await client.close(code, reason)
        except Exception as e:
            self.logger.critical(
                f"Unexpected exception was raised while closing connection to client {client.snowflake}: {e}"
            )

    async def execute_close_multi(self, clients, code=1000, reason=""):
        events = [self.execute_close_single(client, code, reason) for client in clients]
        group = self.asyncio.gather(*events)
        await group

    # Deprecated. Provides semi-backwards compatibility for callback functions from 0.1.9.2.
    def bind_callback(self, cmd, schema, method):
        # Create schema category for command event manager
        if schema not in self.command_handlers:
            self.logger.debug(f"Creating protocol {schema.__qualname__} command event manager")
            self.command_handlers[schema] = dict()

        # Create command event handler
        if cmd not in self.command_handlers[schema]:
            self.command_handlers[schema][cmd] = set()

        # Add function to the command handler
        self.logger.debug(f"Binding function {method.__name__} to command {cmd} in {schema.__qualname__} command event manager")
        self.command_handlers[schema][cmd].add(method)
    
    # Deprecated. Provides semi-backwards compatibility for event functions from 0.1.9.2.
    def bind_event(self, event, func):
        match (event):
            case self.on_connect:
                self.on_connect(func)
            case self.on_disconnect:
                self.on_disconnect(func)
            case self.on_error:
                self.on_error(func)
            case self.on_message:
                self.on_message(func)
