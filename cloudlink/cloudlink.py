import websockets
import asyncio
import ujson
import cerberus
import logging
from copy import copy
from snowflake import SnowflakeGenerator

# Import Cloudlink modules
from cloudlink.modules.async_event_manager import async_event_manager
from cloudlink.modules.async_iterables import async_iterable
from cloudlink.modules.clients_manager import clients_manager

# Import builtin schemas to validate the CLPv4 / Scratch Cloud Variable protocol(s)
from cloudlink.modules.schemas import schemas

# Import protocols
from cloudlink.protocols import clpv4
from cloudlink.protocols import scratch


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

        # Websocket server
        self.ws = websockets

        # Components
        self.gen = SnowflakeGenerator(42)
        self.validator = cerberus.Validator()
        self.schemas = schemas
        self.async_iterable = async_iterable
        self.copy = copy
        self.clients_manager = clients_manager(self)
        self.exceptions = exceptions()

        # Create event managers
        self.on_connect_events = async_event_manager(self)
        self.on_message_events = async_event_manager(self)
        self.on_disconnect_events = async_event_manager(self)
        self.on_error_events = async_event_manager(self)
        self.exception_handlers = dict()

        # Create method handlers
        self.command_handlers = dict()

        # Enable scratch protocol support on startup
        self.enable_scratch_support = True

        # Message of the day
        self.enable_motd = False
        self.motd_message = str()

        # Set to -1 to allow as many client as possible
        self.max_clients = -1

    # Runs the server.
    def run(self, ip="127.0.0.1", port=3000):
        try:
            self.logger.info(f"Cloudlink Server v{self.version}")

            # Validate config before startup
            if type(self.max_clients) != int:
                raise TypeError("The max_clients value must be a integer value set to -1 (unlimited clients) or greater than zero!")

            if self.max_clients < -1 or self.max_clients == 0:
                raise ValueError("The max_clients value must be a integer value set to -1 (unlimited clients) or greater than zero!")

            if type(self.enable_scratch_support) != bool:
                raise TypeError("The enable_scratch_support value must be a boolean!")

            if type(self.enable_motd) != bool:
                raise TypeError("The enable_motd value must be a boolean!")

            if type(self.motd_message) != str:
                raise TypeError("The motd_message value must be a string!")

            # Load CLPv4 protocol
            clpv4(self)

            # Load Scratch protocol
            if self.enable_scratch_support:
                scratch(self)

            # Start server
            self.asyncio.run(self.__run__(ip, port))

        except KeyboardInterrupt:
            pass

    # Event binder for on_command events
    def on_command(self, cmd, schema):
        def bind_event(func):

            # Create schema category for command event manager
            if schema not in self.command_handlers:
                self.logger.debug(f"Adding schema {schema.__qualname__} to command handlers")
                self.command_handlers[schema] = dict()

            # Create command event handler
            if cmd not in self.command_handlers[schema]:
                self.logger.debug(f"Creating command handler \"{cmd}\" with schema {schema.__qualname__}")
                self.command_handlers[schema][cmd] = async_event_manager(self)

            # Add function to the command handler
            self.logger.debug(f"Binding function {func.__qualname__} to command handler \"{cmd}\" with schema {schema.__qualname__}")
            self.command_handlers[schema][cmd].bind(func)

        # End on_command binder
        return bind_event

    # Event binder for on_error events with specific shemas/exception types
    def on_exception(self, exception_type, schema):
        def bind_event(func):

            # Create schema category for error event manager
            if schema not in self.exception_handlers:
                self.logger.debug(f"Adding schema {schema.__qualname__} to exception handlers")
                self.exception_handlers[schema] = dict()

            # Create error event handler
            if exception_type not in self.exception_handlers[schema]:
                self.logger.debug(f"Creating exception handler {exception_type} with schema {schema.__qualname__}")
                self.exception_handlers[schema][exception_type] = async_event_manager(self)

            # Add function to the error command handler
            self.logger.debug(
                f"Binding function {func.__qualname__} to exception handler {exception_type} with schema {schema.__qualname__}")
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

    # Friendly version of send_packet_unicast / send_packet_multicast
    def send_packet(self, obj, message):
        if hasattr(obj, "__iter__"):
            self.asyncio.create_task(self.__execute_multicast__(obj, message))
        else:
            self.asyncio.create_task(self.__execute_unicast__(obj, message))

    # Send message to a single client
    def send_packet_unicast(self, client, message):
        # Create unicast task
        self.asyncio.create_task(self.__execute_unicast__(client, message))

    # Send message to multiple clients
    def send_packet_multicast(self, clients, message):
        # Create multicast task
        self.asyncio.create_task(self.__execute_multicast__(clients, message))

    # Close the connection to client(s)
    def close_connection(self, obj, code=1000, reason=""):
        if hasattr(obj, "__iter__"):
            self.asyncio.create_task(self.__execute_close_multi__(obj, code, reason))
        else:
            self.asyncio.create_task(self.__execute_close_single__(obj, code, reason))

    # Message processor
    async def __process__(self, client, message):

        # Empty packet
        if not len(message):

            # Fire on_error events
            asyncio.create_task(self.__execute_on_error_events__(client, self.exceptions.EmptyMessage))

            # Fire exception handling events
            if client.protocol_set:
                self.asyncio.create_task(
                    self.__execute_exception_handlers__(
                        client=client,
                        exception_type=self.exceptions.EmptyMessage,
                        schema=client.protocol,
                        details="Empty message"
                    )
                )

            # End __process__ coroutine
            return

        # Parse JSON in message and convert to dict
        try:
            message = ujson.loads(message)
        except Exception as error:

            # Log JSON parsing error
            self.logger.warning(f"Handling JSON exception: {error}")

            # Fire on_error events
            self.asyncio.create_task(self.__execute_on_error_events__(client, error))

            # Fire exception handling events
            if client.protocol_set:
                self.asyncio.create_task(
                    self.__execute_exception_handlers__(
                        client=client,
                        exception_type=self.exceptions.JSONError,
                        schema=client.protocol,
                        details=f"JSON parsing error: {error}"
                    )
                )

            # End __process__ coroutine
            return

        self.logger.debug(f"Got message from client {client.snowflake}: {message}")

        # Begin validation
        valid = False
        selected_protocol = None

        # Client protocol is unknown
        if not client.protocol:

            # Identify protocol
            errorlist = list()
            for schema in self.command_handlers:
                if self.validator(message, schema.default):
                    valid = True
                    selected_protocol = schema
                    self.logger.debug(f"Validation passed; Detected schema: {selected_protocol}")
                    break
                else:
                    errorlist.append(self.validator.errors)
                    self.logger.debug(f"Validation error: {self.validator.errors}")

            if not valid:
                # Log failed identification
                self.logger.debug(f"Could not identify protocol used by client {client.snowflake}: {errorlist}")

                # Fire on_error events
                self.asyncio.create_task(self.__execute_on_error_events__(client, "Unable to identify protocol"))

                # Close the connection
                await client.send("Unable to identify protocol")
                self.close_connection(client, reason="Unable to identify protocol")

                # End __process__ coroutine
                return

            # Log known protocol
            self.logger.info(f"Client {client.snowflake} is using protocol {selected_protocol.__qualname__}")

            # Make the client's protocol known
            self.clients_manager.set_protocol(client, selected_protocol)

        else:
            # Validate message using known protocol
            selected_protocol = client.protocol

            if not self.validator(message, selected_protocol.default):
                errors = self.validator.errors

                # Log failed validation
                self.logger.debug(f"Client {client.snowflake} sent message that failed validation: {errors}")

                # Fire on_error events
                self.asyncio.create_task(self.__execute_on_error_events__(client, errors))

                # End __process__ coroutine
                return

        # Check if command exists
        if message[selected_protocol.command_key] not in self.command_handlers[selected_protocol]:

            # Log invalid command
            self.logger.warning(f"Invalid command \"{message[selected_protocol.command_key]}\" in protocol {selected_protocol.__qualname__} from client {client.snowflake}")

            # Fire on_error events
            self.asyncio.create_task(self.__execute_on_error_events__(client, "Invalid command"))

            # Fire exception handling events
            if client.protocol_set:
                self.asyncio.create_task(
                    self.__execute_exception_handlers__(
                        client=client,
                        exception_type=self.exceptions.InvalidCommand,
                        schema=client.protocol,
                        details=f"Invalid command: {message[selected_protocol.command_key]}"
                    )
                )

            # End __process__ coroutine
            return

        # Fire on_command events
        self.asyncio.create_task(
            self.__execute_on_command_events__(
                client,
                message,
                selected_protocol
            )
        )

        # Fire on_message events
        self.asyncio.create_task(
            self.__execute_on_message_events__(
                client,
                message
            )
        )

    # Connection handler
    async def __handler__(self, client):
        # Limit the amount of clients connected
        if self.max_clients != -1:
            if len(self.clients_manager) >= self.max_clients:
                self.logger.warning(f"Refusing new connection due to the server being full")
                await client.send("Server is full")
                await client.close(reason="Server is full")
                return
        
        # Startup client attributes
        client.snowflake = str(next(self.gen))
        client.protocol = None
        client.protocol_set = False
        client.rooms = set
        client.username_set = False
        client.friendly_username = str()
        client.linked = False
        
        # Add to clients manager
        self.clients_manager.add(client)

        # Log new connection
        self.logger.info(f"Client {client.snowflake} connected")

        # Log current number of clients
        self.logger.info(f"There are now {len(self.clients_manager)} clients connected.")

        # Fire on_connect events
        self.asyncio.create_task(self.__execute_on_connect_events__(client))

        # Primary asyncio loop for the lifespan of the websocket connection
        try:
            async for message in client:
                await self.__process__(client, message)

        # Handle unexpected disconnects
        except self.ws.exceptions.ConnectionClosedError:
            self.logger.debug(f"Handling ConnectionClosedError exception raised by websocket")

        # Handle OK disconnects
        except self.ws.exceptions.ConnectionClosedOK:
            self.logger.debug(f"Handling ConnectionClosedOK exception raised by websocket")

        # Catch any unexpected exceptions
        except Exception as e:
            self.logger.critical(f"Unexpected exception was raised: {e}")

            # Fire on_error events
            self.asyncio.create_task(self.__execute_on_error_events__(client, f"Unexpected exception was raised: {e}"))

            # Fire exception handling events
            if client.protocol_set:
                self.asyncio.create_task(
                    self.__execute_exception_handlers__(
                        client=client,
                        exception_type=self.exceptions.InternalError,
                        schema=client.protocol,
                        details=f"Unexpected exception was raised: {e}"
                    )
                )

        # Graceful shutdown
        finally:

            # Remove from clients manager
            self.clients_manager.remove(client)

            # Log disconnect
            self.logger.info(f"Client {client.snowflake} disconnected")

            # Log current number of clients
            self.logger.info(f"There are now {len(self.clients_manager)} clients connected.")

            # Fire on_disconnect events
            self.asyncio.create_task(self.__execute_on_disconnect_events__(client))

    # Server Asyncio loop
    async def __run__(self, ip, port):

        # Main event loop
        async with self.ws.serve(self.__handler__, ip, port):
            await self.asyncio.Future()

    # Asyncio event-handling coroutines
    async def __execute_on_disconnect_events__(self, client):
        self.logger.debug(f"Firing all events bound to on_disconnect")
        async for event in self.on_disconnect_events:
            await event(client)

    async def __execute_on_connect_events__(self, client):
        self.logger.debug(f"Firing all events bound to on_connect")
        async for event in self.on_connect_events:
            await event(client)

    async def __execute_on_message_events__(self, client, message):
        self.logger.debug(f"Firing all events bound to on_message")
        async for event in self.on_message_events:
            await event(client, message)

    async def __execute_on_command_events__(self, client, message, schema):
        self.logger.debug(f"Firing all bound events to command handler \"{message[schema.command_key]}\" with schema {schema.__qualname__}")
        async for event in self.command_handlers[schema][message[schema.command_key]]:
            await event(client, message)

    async def __execute_on_error_events__(self, client, errors):
        self.logger.debug(f"Firing all events bound to on_error")
        async for event in self.on_error_events:
            await event(client, errors)

    async def __execute_exception_handlers__(self, client, exception_type, schema, details):
        # Guard clauses
        if schema not in self.exception_handlers:
            return
        if exception_type not in self.exception_handlers[schema]:
            return
        
        self.logger.debug(f"Firing all exception handlers bound to schema {schema.__qualname__} and exception type {exception_type}")
        
        # Fire events
        async for event in self.exception_handlers[schema][exception_type]:
            await event(client, details)

    async def __execute_unicast__(self, client, message):
        self.logger.debug(f"Sending unicast message {message} to {client.snowflake}")
        await client.send(ujson.dumps(message))

    async def __execute_multicast__(self, clients, message):
        self.logger.debug(f"Sending multicast message {message} to {len(clients)} clients")
        async for client in self.async_iterable(self, clients):
            await client.send(ujson.dumps(message))

    async def __execute_close_single__(self, client, code=1000, reason=""):
        self.logger.debug(f"Closing the connection to client {client.snowflake} with code {code} and reason {reason}")
        await client.close(code, reason)

    async def __execute_close_multi__(self, clients, code=1000, reason=""):
        self.logger.debug(f"Closing the connection to {len(clients)} clients with code {code} and reason {reason}")
        async for client in self.async_iterable(self, clients):
            await client.close(code, reason)
