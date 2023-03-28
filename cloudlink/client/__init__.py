# Core components of the CloudLink client
import asyncio
import ssl

import cerberus
import logging
import time
from copy import copy

# Import websockets and SSL support
import websockets

# Import shared modules
from cloudlink.shared_modules.async_event_manager import async_event_manager
from cloudlink.shared_modules.async_iterables import async_iterable

# Import JSON library - Prefer UltraJSON but use native JSON if failed
try:
    import ujson
except ImportError:
    print("Server failed to import UltraJSON, failing back to native JSON library.")
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
class client:
    def __init__(self):
        self.version = "0.2.0"

        # Logging
        self.logging = logging
        self.logger = self.logging.getLogger(__name__)

        # Asyncio
        self.asyncio = asyncio

        # Configure websocket framework
        self.ws = websockets
        self.client = None

        # Components
        self.ujson = ujson
        self.validator = cerberus.Validator()
        self.async_iterable = async_iterable
        self.copy = copy
        self.exceptions = exceptions()

        # Dictionary containing protocols as keys and sets of commands as values
        self.disabled_commands = dict()

        # Create event managers
        self.on_connect_events = async_event_manager(self)
        self.on_message_events = async_event_manager(self)
        self.on_disconnect_events = async_event_manager(self)
        self.on_error_events = async_event_manager(self)
        self.exception_handlers = dict()

        # Create method handlers
        self.command_handlers = dict()

        # Configure framework logging
        self.suppress_websocket_logs = True

        # Configure SSL support
        self.ssl_enabled = False
        self.ssl_context = None

    # Enables SSL support
    def enable_ssl(self, certfile):
        try:
            self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            self.ssl_context.load_verify_locations(certfile)
            self.ssl_enabled = True
            self.logger.info(f"SSL support initialized!")
        except Exception as e:
            self.logger.error(f"Failed to initialize SSL support! {e}")

    # Runs the client.
    def run(self, host="ws://127.0.0.1:3000"):
        try:
            # Startup message
            self.logger.info(f"CloudLink {self.version} - Now connecting to {host}")

            # Suppress websocket library logging
            if self.suppress_websocket_logs:
                self.logging.getLogger('asyncio').setLevel(self.logging.ERROR)
                self.logging.getLogger('asyncio.coroutines').setLevel(self.logging.ERROR)
                self.logging.getLogger('websockets.client').setLevel(self.logging.ERROR)
                self.logging.getLogger('websockets.protocol').setLevel(self.logging.ERROR)

            # Start server
            self.asyncio.run(self.__run__(host))

        except KeyboardInterrupt:
            pass

    # Event binder for on_command events
    def on_command(self, cmd, schema):
        def bind_event(func):

            # Create schema category for command event manager
            if schema not in self.command_handlers:
                self.logger.info(f"Creating protocol {schema.__qualname__} command event manager")
                self.command_handlers[schema] = dict()

            # Create command event handler
            if cmd not in self.command_handlers[schema]:
                self.command_handlers[schema][cmd] = async_event_manager(self)

            # Add function to the command handler
            self.command_handlers[schema][cmd].bind(func)

        # End on_command binder
        return bind_event

    # Event binder for on_error events with specific shemas/exception types
    def on_exception(self, exception_type, schema):
        def bind_event(func):

            # Create schema category for error event manager
            if schema not in self.exception_handlers:
                self.logger.info(f"Creating protocol {schema.__qualname__} exception event manager")
                self.exception_handlers[schema] = dict()

            # Create error event handler
            if exception_type not in self.exception_handlers[schema]:
                self.exception_handlers[schema][exception_type] = async_event_manager(self)

            # Add function to the error command handler
            self.exception_handlers[schema][exception_type].bind(func)

        # End on_error_specific binder
        return bind_event

    # Event binder for on_message events
    def on_message(self, func):
        self.on_message_events.bind(func)

    # Event binder for on_connect events.
    def on_connect(self, func):
        self.on_connect_events.bind(func)

    # Event binder for on_disconnect events.
    def on_disconnect(self, func):
        self.on_disconnect_events.bind(func)

    # Event binder for on_error events.
    def on_error(self, func):
        self.on_error_events.bind(func)

    # Send message
    def send_packet(self, message):
        # Create unicast task
        self.asyncio.create_task(self.execute_send(message))

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
            self.logger.debug(f"Server sent empty message ")

            # Fire on_error events
            asyncio.create_task(self.execute_on_error_events(self.exceptions.EmptyMessage))

            # Fire exception handling events
            self.asyncio.create_task(
                self.execute_exception_handlers(
                    exception_type=self.exceptions.EmptyMessage,
                    schema=client.protocol,
                    details="Empty message"
                )
            )

            # End message_processor coroutine
            return

        # Parse JSON in message and convert to dict
        try:
            message = self.ujson.loads(message)

        except Exception as error:
            self.logger.debug(f"Server sent invalid JSON: {error}")

            # Fire on_error events
            self.asyncio.create_task(self.execute_on_error_events(error))

            # Fire exception handling events
            if client.protocol_set:
                self.asyncio.create_task(
                    self.execute_exception_handlers(
                        exception_type=self.exceptions.JSONError,
                        schema=client.protocol,
                        details=error
                    )
                )

            else:
                # Close the connection
                self.send_packet("Invalid JSON")
                self.close_connection(client, reason="Invalid JSON")

            # End message_processor coroutine
            return

        # Begin validation
        valid = False
        selected_protocol = None

        # Client protocol is unknown
        if not client.protocol:
            self.logger.debug(f"Trying to identify server's protocol")

            # Identify protocol
            errorlist = list()

            for schema in self.command_handlers:
                if self.validator(message, schema.default):
                    valid = True
                    selected_protocol = schema
                    break
                else:
                    errorlist.append(self.validator.errors)

            if not valid:
                # Log failed identification
                self.logger.debug(f"Could not identify protocol used by server: {errorlist}")

                # Fire on_error events
                self.asyncio.create_task(self.execute_on_error_events("Unable to identify protocol"))

                # Close the connection
                self.send_packet("Unable to identify protocol")
                self.close_connection(client, reason="Unable to identify protocol")

                # End message_processor coroutine
                return

            # Log known protocol
            self.logger.debug(f"Server is using protocol {selected_protocol.__qualname__}")

        else:
            self.logger.debug(
                f"Validating message from server using protocol {client.protocol.__qualname__}")

            # Validate message using known protocol
            selected_protocol = client.protocol

            if not self.validator(message, selected_protocol.default):
                errors = self.validator.errors

                # Log failed validation
                self.logger.debug(f"Server sent message that failed validation: {errors}")

                # Fire on_error events
                self.asyncio.create_task(self.execute_on_error_events(errors))

                # Fire exception handling events
                if client.protocol_set:
                    self.asyncio.create_task(
                        self.execute_exception_handlers(
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
                f"Server sent an invalid command \"{message[selected_protocol.command_key]}\" in protocol {selected_protocol.__qualname__}")

            # Fire on_error events
            self.asyncio.create_task(self.execute_on_error_events("Invalid command"))

            # Fire exception handling events
            if client.protocol_set:
                self.asyncio.create_task(
                    self.execute_exception_handlers(
                        exception_type=self.exceptions.InvalidCommand,
                        schema=client.protocol,
                        details=message[selected_protocol.command_key]
                    )
                )

            # End message_processor coroutine
            return

        # Fire on_command events
        self.asyncio.create_task(
            self.execute_on_command_events(
                message,
                selected_protocol
            )
        )

        # Fire on_message events
        self.asyncio.create_task(
            self.execute_on_message_events(
                message
            )
        )

    # Connection handler
    async def connection_handler(self, client):

        # Startup client attributes
        client.snowflake = str()
        client.protocol = None
        client.protocol_set = False
        client.rooms = set()
        client.username_set = False
        client.username = str()
        client.handshake = False

        # Begin tracking the lifetime of the client
        client.birth_time = time.monotonic()

        # Fire on_connect events
        self.asyncio.create_task(self.execute_on_connect_events())

        self.logger.debug(f"Client connected")

        # Run connection loop
        await self.connection_loop(client)

        # Fire on_disconnect events
        self.asyncio.create_task(self.execute_on_disconnect_events())

        self.logger.debug(
            f"Client disconnected: Total lifespan of {time.monotonic() - client.birth_time} seconds.")

    # Connection loop - Redefine for use with another outside library
    async def connection_loop(self, client):
        # Primary asyncio loop for the lifespan of the websocket connection
        try:
            async for message in client:
                # Start keeping track of processing time
                start = time.perf_counter()
                self.logger.debug(f"Now processing message from server...")

                # Process the message
                await self.message_processor(client, message)

                # Log processing time
                self.logger.debug(
                    f"Done processing message from server. Processing took {time.perf_counter() - start} seconds.")

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
            self.asyncio.create_task(self.execute_on_error_events(f"Unexpected exception was raised: {e}"))

            # Fire exception handling events
            self.asyncio.create_task(
                self.execute_exception_handlers(
                    exception_type=self.exceptions.InternalError,
                    schema=client.protocol,
                    details=f"Unexpected exception was raised: {e}"
                )
            )

    # WebSocket-specific server loop
    async def __run__(self, host):
        async with self.ws.connect(host) as self.client:
            await self.connection_handler(self.client)

    # Asyncio event-handling coroutines

    async def execute_on_disconnect_events(self):
        async for event in self.on_disconnect_events:
            await event()

    async def execute_on_connect_events(self):
        async for event in self.on_connect_events:
            await event()

    async def execute_on_message_events(self, message):
        async for event in self.on_message_events:
            await event(message)

    async def execute_on_command_events(self, message, schema):
        async for event in self.command_handlers[schema][message[schema.command_key]]:
            await event(message)

    async def execute_on_error_events(self, errors):
        async for event in self.on_error_events:
            await event(errors)

    async def execute_exception_handlers(self, exception_type, schema, details):
        # Guard clauses
        if schema not in self.exception_handlers:
            return
        if exception_type not in self.exception_handlers[schema]:
            return

        # Fire events
        async for event in self.exception_handlers[schema][exception_type]:
            await event(details)


    # WebSocket-specific coroutines

    async def execute_send(self, message):
        # Convert dict to JSON
        if type(message) == dict:
            message = self.ujson.dumps(message)
        await self.client.send(message)
