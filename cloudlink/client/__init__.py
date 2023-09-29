# Core components of the CloudLink client
import asyncio
import ssl
import cerberus
import logging
import time
from copy import copy

# Import websockets and SSL support
import websockets

# Import shared module
from ..async_iterables import async_iterable

# Import JSON library - Prefer UltraJSON but use native JSON if failed
try:
    import ujson
except Exception as e:
    print(f"Client failed to import UltraJSON, failing back to native JSON library. Exception code: {e}")
    import json as ujson

# Import required CL4 client protocol
from . import protocol, schema


# Define server exceptions
class exceptions:
    class EmptyMessage(Exception):
        """This exception is raised when a client receives an empty packet."""
        pass

    class UnknownCommand(Exception):
        """This exception is raised when the server sends a command that the client does not recognize."""
        pass

    class JSONError(Exception):
        """This exception is raised when the client fails to parse the server message's JSON."""
        pass

    class ValidationError(Exception):
        """This exception is raised when the server sends a message that fails validation before execution."""
        pass

    class InternalError(Exception):
        """This exception is raised when an unexpected and/or unhandled exception is raised."""
        pass

    class ListenerExists(Exception):
        """This exception is raised when attempting to process a listener that already has an existing listener instance."""
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
        self.validator = cerberus.Validator
        self.async_iterable = async_iterable
        self.exceptions = exceptions
        self.copy = copy

        # Create event managers
        self.on_initial_connect_events = set()
        self.on_full_connect_events = set()
        self.on_message_events = set()
        self.on_disconnect_events = set()
        self.on_error_events = set()
        self.exception_handlers = dict()
        self.listener_events_await_specific = dict()
        self.listener_events_decorator_specific = dict()
        self.listener_responses = dict()
        self.on_username_set_events = set()

        # Prepare command event handlers
        self.protocol_command_handlers = dict()
        for cmd in [
            "ping", 
            "gmsg", 
            "gvar", 
            "pmsg", 
            "pvar",
            "statuscode",
            "client_obj",
            "client_ip",
            "server_version",
            "ulist",
            "direct"
        ]:
            self.protocol_command_handlers[cmd] = set()

        # Create method handlers
        self.command_handlers = dict()

        # Configure framework logging
        self.suppress_websocket_logs = True

        # Configure SSL support
        self.ssl_enabled = False
        self.ssl_context = None

        # Load built-in protocol
        self.schema = schema.schema
        self.protocol = protocol.clpv4(self)

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

            # Start client
            self.asyncio.run(self.__run__(host))

        except KeyboardInterrupt:
            pass

    # Event binder for on_command events
    def on_command(self, cmd):
        def bind_event(func):

            # Create command event handler
            if cmd not in self.command_handlers:
                self.command_handlers[cmd] = set()

            # Add function to the command handler
            self.command_handlers[cmd].add(func)

        # End on_command binder
        return bind_event

    # Credit to @ShowierData9978 for this: Listen for messages containing specific "listener" keys
    async def wait_for_listener(self, listener_id):
        # Prevent listener collision
        if listener_id in self.listener_events_await_specific:
            raise self.exceptions.ListenerExists(f"The listener {listener_id} is already being awaited. Please use a different listener ID.")

        # Create a new event object.
        event = self.asyncio.Event()

        # Register the event so that the client can continue listening for messages.
        self.listener_events_await_specific[listener_id] = event

        # Create the waiter task.
        task = self.asyncio.create_task(
            self.listener_waiter(
                listener_id,
                event
            )
        )

        # Wait for the waiter task to finish.
        await task

        # Get the response
        response = self.copy(self.listener_responses[listener_id])

        # Remove from the listener events dict.
        self.listener_events_await_specific.pop(listener_id)

        # Free up listener responses
        self.listener_responses.pop(listener_id)

        # Return the response
        return response

    def on_username_set(self, func):
        self.on_username_set_events.add(func)

    # Version of the wait for listener tool for decorator usage.
    def on_listener(self, listener_id):
        def bind_event(func):

            # Create listener event handler
            if listener_id not in self.listener_events_decorator_specific:
                self.listener_events_decorator_specific[listener_id] = set()

            # Add function to the listener handler
            self.listener_events_decorator_specific[listener_id].add(func)

        # End on_listener binder
        return bind_event

    # Event binder for on_error events with specific schemas/exception types
    def on_exception(self, exception_type):
        def bind_event(func):

            # Create error event handler
            if exception_type not in self.exception_handlers:
                self.exception_handlers[exception_type] = set()

            # Add function to the error command handler
            self.exception_handlers[exception_type].add(func)

        # End on_error_specific binder
        return bind_event

    # Event binder for on_message events
    def on_message(self, func):
        self.on_message_events.add(func)

    # Event binder for starting up the client.
    def on_initial_connect(self, func):
        self.on_initial_connect_events.add(func)

    # Event binder for on_connect events.
    def on_connect(self, func):
        self.on_full_connect_events.add(func)

    # Event binder for on_disconnect events.
    def on_disconnect(self, func):
        self.on_disconnect_events.add(func)

    # Event binder for on_error events.
    def on_error(self, func):
        self.on_error_events.add(func)

    # CL4 client-specific command events

    # Event binder for gmsg events.
    def on_gmsg(self, func):
        self.logger.debug(f"Binding function {func.__name__} to gmsg command event manager")
        self.protocol_command_handlers["gmsg"].add(func)
    
    # Event binder for pmsg events.
    def on_pmsg(self, func):
        self.logger.debug(f"Binding function {func.__name__} to pmsg command event manager")
        self.protocol_command_handlers["pmsg"].add(func)
    
    # Event binder for gvar events.
    def on_gvar(self, func):
        self.logger.debug(f"Binding function {func.__name__} to gvar command event manager")
        self.protocol_command_handlers["gvar"].add(func)
    
    # Event binder for pvar events.
    def on_pvar(self, func):
        self.logger.debug(f"Binding function {func.__name__} to pvar command event manager")
        self.protocol_command_handlers["pvar"].add(func)
    
    # Event binder for direct events.
    def on_direct(self, func):
        self.logger.debug(f"Binding function {func.__name__} to direct command event manager")
        self.protocol_command_handlers["direct"].add(func)
    
    # Event binder for statuscode events.
    def on_statuscode(self, func):
        self.logger.debug(f"Binding function {func.__name__} to statuscode command event manager")
        self.protocol_command_handlers["statuscode"].add(func)
    
    # Event binder for client_obj events.
    def on_client_obj(self, func):
        self.logger.debug(f"Binding function {func.__name__} to client_obj command event manager")
        self.protocol_command_handlers["client_obj"].add(func)

    # Event binder for client_ip events.
    def on_client_ip(self, func):
        self.logger.debug(f"Binding function {func.__name__} to client_ip command event manager")
        self.protocol_command_handlers["client_ip"].add(func)
    
    # Event binder for server_version events.
    def on_server_version(self, func):
        self.logger.debug(f"Binding function {func.__name__} to server_version command event manager")
        self.protocol_command_handlers["server_version"].add(func)
    
    # Event binder for ulist events.
    def on_ulist(self, func):
        self.logger.debug(f"Binding function {func.__name__} to ulist command event manager")
        self.protocol_command_handlers["ulist"].add(func)

    # Send message
    def send_packet(self, message):
        self.asyncio.create_task(self.execute_send(message))

    # Send message and wait for a response
    async def send_packet_and_wait(self, message):
        self.logger.debug(f"Sending message containing listener {message['listener']}...")
        await self.execute_send(message)
        response = await self.wait_for_listener(message["listener"])
        return response

    # Close the connection
    def disconnect(self, code=1000, reason=""):
        self.asyncio.create_task(self.execute_disconnect(code, reason))

    # Message processor
    async def message_processor(self, message):

        # Empty packet
        if not len(message):
            self.logger.debug(f"Server sent empty message ")

            # Fire on_error events
            asyncio.create_task(self.execute_on_error_events(self.exceptions.EmptyMessage))

            # Fire exception handling events
            self.asyncio.create_task(
                self.execute_exception_handlers(
                    exception_type=self.exceptions.EmptyMessage,
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
            if self.client.protocol_set:
                self.asyncio.create_task(
                    self.execute_exception_handlers(
                        exception_type=self.exceptions.JSONError,
                        details=error
                    )
                )

            else:
                # Close the connection
                self.send_packet("Invalid JSON")
                self.close_connection(reason="Invalid JSON")

            # End message_processor coroutine
            return

        # Begin validation
        validator = self.validator(self.schema.default, allow_unknown=True)
        if not validator.validate(message):
            errors = validator.errors

            # Log failed validation
            self.logger.debug(f"Server sent message that failed validation: {errors}")

            # Fire on_error events
            self.asyncio.create_task(self.execute_on_error_events(errors))

            # Fire exception handling events
            if self.client.protocol_set:
                self.asyncio.create_task(
                    self.execute_exception_handlers(
                        exception_type=self.exceptions.ValidationError,
                        details=errors
                    )
                )

            # End message_processor coroutine
            return

        # Check if command exists
        if message["cmd"] not in self.command_handlers:

            # Log invalid command
            self.logger.debug(f"Server sent an unknown command \"{message['cmd']}\"")

            # Fire on_error events
            self.asyncio.create_task(self.execute_on_error_events("Unknown command"))

            # Fire exception handling events
            if self.client.protocol_set:
                self.asyncio.create_task(
                    self.execute_exception_handlers(
                        exception_type=self.exceptions.InvalidCommand,
                        details=message["cmd"]
                    )
                )

            # End message_processor coroutine
            return

        # Check if the message contains listeners
        if "listener" in message:
            if message["listener"] in self.listener_events_await_specific:
                # Fire awaiting listeners
                self.logger.debug(f"Received message containing listener {message['listener']}!")
                self.listener_responses[message["listener"]] = message
                self.listener_events_await_specific[message["listener"]].set()

            elif message["listener"] in self.listener_events_decorator_specific:
                # Fire all decorator-based listeners
                self.asyncio.create_task(
                    self.execute_on_listener_events(
                        message
                    )
                )

        # Fire on_command events
        self.asyncio.create_task(
            self.execute_on_command_events(
                message
            )
        )

        # Fire on_message events
        self.asyncio.create_task(
            self.execute_on_message_events(
                message
            )
        )

    # Connection handler
    async def connection_handler(self):

        # Startup client attributes
        self.client.snowflake = str()
        self.client.protocol = None
        self.client.protocol_set = False
        self.client.rooms = set()
        self.client.username_set = False
        self.client.username = str()
        self.client.handshake = False

        # Begin tracking the lifetime of the client
        self.client.birth_time = time.monotonic()

        # Fire on_connect events
        self.asyncio.create_task(self.execute_on_initial_connect_events())

        self.logger.debug(f"Client connected")

        # Run connection loop
        await self.connection_loop()

        # Fire on_disconnect events
        self.asyncio.create_task(self.execute_on_disconnect_events())

        self.logger.debug(
            f"Client disconnected: Total lifespan of {time.monotonic() - self.client.birth_time} seconds.")

    # Connection loop - Redefine for use with another outside library
    async def connection_loop(self):
        # Primary asyncio loop for the lifespan of the websocket connection
        try:
            async for message in self.client:
                # Start keeping track of processing time
                start = time.perf_counter()
                self.logger.debug(f"Now processing message from server...")

                # Process the message
                await self.message_processor(message)

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
                    details=f"Unexpected exception was raised: {e}"
                )
            )

    # WebSocket-specific server loop
    async def __run__(self, host):
        async with self.ws.connect(host) as self.client:
            await self.connection_handler()

    # Asyncio event-handling coroutines

    async def execute_on_username_set_events(self, id, username, uuid):
        events = [event(id, username, uuid) for event in self.on_username_set_events]
        group = self.asyncio.gather(*events)
        await group

    async def execute_on_disconnect_events(self):
        events = [event() for event in self.on_disconnect_events]
        group = self.asyncio.gather(*events)
        await group

    async def execute_on_initial_connect_events(self):
        events = [event() for event in self.on_initial_connect_events]
        group = self.asyncio.gather(*events)
        await group

    async def execute_on_full_connect_events(self):
        events = [event() for event in self.on_full_connect_events]
        group = self.asyncio.gather(*events)
        await group

    async def execute_on_message_events(self, message):
        events = [event(message) for event in self.on_message_events]
        group = self.asyncio.gather(*events)
        await group

    async def execute_on_command_events(self, message):
        events = [event(message) for event in self.command_handlers[message["cmd"]]]
        group = self.asyncio.gather(*events)
        await group

    async def execute_on_listener_events(self, message):
        events = [event(message) for event in self.listener_events_decorator_specific[message["listener"]]]
        group = self.asyncio.gather(*events)
        await group

    async def execute_on_error_events(self, errors):
        events = [event(errors) for event in self.on_error_events]
        group = self.asyncio.gather(*events)
        await group

    async def execute_exception_handlers(self, exception_type, details):
        # Guard clauses
        if exception_type not in self.exception_handlers:
            return

        # Fire events
        events = [event(details) for event in self.exception_handlers[exception_type]]
        group = self.asyncio.gather(*events)
        await group

    async def listener_waiter(self, listener_id, event):
        await event.wait()

    # WebSocket-specific coroutines

    async def execute_disconnect(self, code=1000, reason=""):
        await self.client.close(code, reason)

    async def execute_send(self, message):
        # Convert dict to JSON
        if type(message) == dict:
            message = self.ujson.dumps(message)
        await self.client.send(message)
