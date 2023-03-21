# Core components of the CloudLink engine
import asyncio
import ujson
import cerberus
import logging
from copy import copy
from snowflake import SnowflakeGenerator

# Import websocket engine
import websockets

# Import CloudLink modules
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

        # Configure websocket framework
        self.ws = websockets
        self.ujson = ujson

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
        
        # Configure framework logging
        self.supress_websocket_logs = True
        
        # Set to -1 to allow as many client as possible
        self.max_clients = -1
    
    # Runs the server.
    def run(self, ip="127.0.0.1", port=3000):
        try:
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
            
            # Startup message
            self.logger.info(f"CloudLink {self.version} - Now listening to {ip}:{port}")
            
            # Supress websocket library logging
            if self.supress_websocket_logs:
                self.logging.getLogger('asyncio').setLevel(self.logging.ERROR)
                self.logging.getLogger('asyncio.coroutines').setLevel(self.logging.ERROR)
                self.logging.getLogger('websockets.server').setLevel(self.logging.ERROR)
                self.logging.getLogger('websockets.protocol').setLevel(self.logging.ERROR)
            
            # Start server
            self.asyncio.run(self.__run__(ip, port))
            

        except KeyboardInterrupt:
            pass

    # Event binder for on_command events
    def on_command(self, cmd, schema):
        def bind_event(func):

            # Create schema category for command event manager
            if schema not in self.command_handlers:
                self.logger.info(f"Creating command event manager {schema.__qualname__}")
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
                self.logger.info(f"Creating exception event manager {schema.__qualname__}")
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
                        details=f"JSON parsing error: {error}"
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
            
            self.logger.debug(f"Checking for protocol using loaded handlers: {self.command_handlers}")
            
            for schema in self.command_handlers:
                if self.validator(message, schema.default):
                    valid = True
                    selected_protocol = schema
                    break
                else:
                    errorlist.append(self.validator.errors)

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

        else:
            self.logger.debug(f"Validating client {client.snowflake}'s message using known protocol: {client.protocol.__qualname__}")
            
            # Validate message using known protocol
            selected_protocol = client.protocol

            if not self.validator(message, selected_protocol.default):
                errors = self.validator.errors

                # Log failed validation
                self.logger.debug(f"Client {client.snowflake} sent message that failed validation: {errors}")

                # Fire on_error events
                self.asyncio.create_task(self.execute_on_error_events(client, errors))

                # End message_processor coroutine
                return

        # Check if command exists
        if message[selected_protocol.command_key] not in self.command_handlers[selected_protocol]:

            # Log invalid command
            self.logger.debug(f"Invalid command \"{message[selected_protocol.command_key]}\" in protocol {selected_protocol.__qualname__} from client {client.snowflake}")

            # Fire on_error events
            self.asyncio.create_task(self.execute_on_error_events(client, "Invalid command"))

            # Fire exception handling events
            if client.protocol_set:
                self.asyncio.create_task(
                    self.execute_exception_handlers(
                        client=client,
                        exception_type=self.exceptions.InvalidCommand,
                        schema=client.protocol,
                        details=f"Invalid command: {message[selected_protocol.command_key]}"
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
        client.rooms = set
        client.username_set = False
        client.friendly_username = str()
        client.linked = False
        
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
        
        self.logger.debug(f"Client {client.snowflake} disconnected")
    
    # Connection loop - Redefine for use with another outside library
    async def connection_loop(self, client):
        # Primary asyncio loop for the lifespan of the websocket connection
        try:
            async for message in client:
                await self.message_processor(client, message)

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
    
    # Server - You can modify this code to use a different websocket engine.
    async def __run__(self, ip, port):
        # Main event loop
        async with self.ws.serve(self.connection_handler, ip, port):
            await self.asyncio.Future()

    # Asyncio event-handling coroutines
    
    async def execute_on_disconnect_events(self, client):
        async for event in self.on_disconnect_events:
            await event(client)

    async def execute_on_connect_events(self, client):
        async for event in self.on_connect_events:
            await event(client)

    async def execute_on_message_events(self, client, message):
        async for event in self.on_message_events:
            await event(client, message)

    async def execute_on_command_events(self, client, message, schema):
        async for event in self.command_handlers[schema][message[schema.command_key]]:
            await event(client, message)

    async def execute_on_error_events(self, client, errors):
        async for event in self.on_error_events:
            await event(client, errors)
    
    async def execute_exception_handlers(self, client, exception_type, schema, details):
        # Guard clauses
        if schema not in self.exception_handlers:
            return
        if exception_type not in self.exception_handlers[schema]:
            return
        
        # Fire events
        async for event in self.exception_handlers[schema][exception_type]:
            await event(client, details)
    
    # You can modify the code below to use different websocket engines.
    
    async def execute_unicast(self, client, message):
    
        # Guard clause
        if type(message) not in [dict, str]:
            raise TypeError("Supported datatypes for messages are dicts and strings, got type {type(message)}.")
        
        # Convert dict to JSON
        if type(message) == dict:
            message = self.ujson.dumps(message)
        
        # Attempt to send the packet
        try:
            await client.send(message)
        except:
            pass
    
    async def execute_multicast(self, clients, message):
        
        # Guard clause
        if type(message) not in [dict, str]:
            raise TypeError("Supported datatypes for messages are dicts and strings, got type {type(message)}.")
        
        # Convert dict to JSON
        if type(message) == dict:
            message = self.ujson.dumps(message)
        
        # Attempt to broadcast the packet
        async for client in self.async_iterable(self, clients):
            try:
                await self.execute_unicast(client, message)
            except:
                pass
    
    async def execute_close_single(self, client, code=1000, reason=""):
        await client.close(code, reason)

    async def execute_close_multi(self, clients, code=1000, reason=""):
        async for client in self.async_iterable(self, clients):
            await self.execute_close_single(client, code, reason)
