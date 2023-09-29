from cloudlink import server
from cloudlink.server.protocols import clpv4, scratch
import asyncio


class example_callbacks:
    def __init__(self, parent):
        self.parent = parent

    async def test1(self, client, message):
        print("Test1!")
        await asyncio.sleep(1)
        print("Test1 after one second!")
    
    async def test2(self, client, message):
        print("Test2!")
        await asyncio.sleep(1)
        print("Test2 after one second!")
    
    async def test3(self, client, message):
        print("Test3!")


class example_commands:
    def __init__(self, parent, protocol):
        
        # Creating custom commands - This example adds a custom command called "foobar".
        @server.on_command(cmd="foobar", schema=protocol.schema)
        async def foobar(client, message):
            print("Foobar!")

            # Reading the IP address of the client is as easy as calling get_client_ip from the clpv4 protocol object.
            print(protocol.get_client_ip(client))

            # In case you need to report a status code, use send_statuscode.
            protocol.send_statuscode(
                client=client,
                code=protocol.statuscodes.ok,
                message=message
            )


class example_events:
    def __init__(self):
        pass

    async def on_close(self, client):
        print("Client", client.id, "disconnected.")

    async def on_connect(self, client):
        print("Client", client.id, "connected.") 


if __name__ == "__main__":
    # Initialize the server
    server = server()
    
    # Configure logging settings
    server.logging.basicConfig(
        level=server.logging.DEBUG
    )

    # Load protocols
    clpv4 = clpv4(server)
    scratch = scratch(server)

    # Load examples
    callbacks = example_callbacks(server)
    commands = example_commands(server, clpv4)
    events = example_events()

    # Binding callbacks - This example binds the "handshake" command with example callbacks.
    # You can bind as many functions as you want to a callback, but they must use async.
    # To bind callbacks to built-in methods (example: gmsg), see cloudlink.cl_methods.
    server.bind_callback(cmd="handshake", schema=clpv4.schema, method=callbacks.test1)
    server.bind_callback(cmd="handshake", schema=clpv4.schema, method=callbacks.test2)

    # Binding events - This example will print a client connect/disconnect message.
    # You can bind as many functions as you want to an event, but they must use async.
    # To see all possible events for the server, see cloudlink.events.
    server.bind_event(server.on_connect, events.on_connect)
    server.bind_event(server.on_disconnect, events.on_close)

    # You can also bind an event to a custom command. We'll bind callbacks.test3 to our 
    # foobar command from earlier.
    server.bind_callback(cmd="foobar", schema=clpv4.schema, method=callbacks.test3)

    # Initialize SSL support
    # server.enable_ssl(certfile="cert.pem", keyfile="privkey.pem")
    
    # Start the server
    server.run(ip="127.0.0.1", port=3000)
