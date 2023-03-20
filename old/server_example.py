from cloudlink import cloudlink


class example_callbacks:
    def __init__(self, parent):
        self.parent = parent

    async def test1(self, client, message, listener):
        print("Test1!")
        await self.parent.asyncio.sleep(1)
        print("Test1 after one second!")

    async def test2(self, client, message, listener):
        print("Test2!")
        await self.parent.asyncio.sleep(1)
        print("Test2 after one second!")

    async def test3(self, client, message, listener):
        print("Test3!")


class example_events:
    def __init__(self):
        pass

    async def on_close(self, client):
        print("Client", client.id, "disconnected.")

    async def on_connect(self, client):
        print("Client", client.id, "connected.")


class example_commands:
    def __init__(self, parent):
        self.parent = parent
        self.supporter = parent.supporter

        # If you want to have commands with very specific formatting, use the validate() function.
        self.validate = parent.validate

        # Various ways to send messages
        self.send_packet_unicast = parent.send_packet_unicast
        self.send_packet_multicast = parent.send_packet_multicast
        self.send_packet_multicast_variable = parent.send_packet_multicast_variable
        self.send_code = parent.send_code

    async def foobar(self, client, message, listener):
        print("Foobar!")

        # Reading the IP address of the client is as easy as calling get_client_ip from the server object.
        print(self.parent.get_client_ip(client))

        # In case you need to report a status code, use send_code.
        await self.send_code(
            client=client,
            code="OK",
            listener=listener
        )


if __name__ == "__main__":
    # Initialize Cloudlink. You will only need to initialize one instance of the main cloudlink module.
    cl = cloudlink()

    # Create a new server object. This supports initializing many servers at once.
    server = cl.server(logs=True)

    # Create examples for various ways to extend the functionality of Cloudlink Server.
    callbacks = example_callbacks(server)
    commands = example_commands(server)
    events = example_events()

    # Set the message-of-the-day.
    server.set_motd("CL4 Optimized! Gotta Go Fast!", True)

    # Here are some extra parameters you can specify to change the functionality of the server.

    # Defaults to empty list. Requires having check_ip_addresses set to True.
    # server.ip_blocklist = ["127.0.0.1"]

    # Defaults to False. If True, the server will refuse all connections until False.
    # server.reject_clients = False

    # Defaults to False. If True, client IP addresses will be resolved and stored until a client disconnects.
    # server.check_ip_addresses = True

    # Defaults to True. If True, the server will support Scratch's cloud variable protocol.
    # server.enable_scratch_support = False

    # Binding callbacks - This example binds the "handshake" command with example callbacks.
    # You can bind as many functions as you want to a callback, but they must use async.
    # To bind callbacks to built-in methods (example: gmsg), see cloudlink.cl_methods.
    server.bind_callback(server.cl_methods.handshake, callbacks.test1)
    server.bind_callback(server.cl_methods.handshake, callbacks.test2)

    # Binding events - This example will print a client connect/disconnect message.
    # You can bind as many functions as you want to an event, but they must use async.
    # To see all possible events for the server, see cloudlink.events.
    server.bind_event(server.events.on_connect, events.on_connect)
    server.bind_event(server.events.on_close, events.on_close)

    # Creating custom commands - This example adds a custom command "foobar" from example_commands
    # and then binds the callback test3 to the new command.
    server.load_custom_methods(commands)
    server.bind_callback(commands.foobar, callbacks.test3)

    # Run the server.
    server.run(ip="localhost", port=3000)
