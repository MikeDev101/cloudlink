from cloudlink import cloudlink


class example_events:
    def __init__(self):
        pass

    def on_connect(self, client):
        print(f"Client {client.obj_id} connected")
        client.set_username(str(client.obj_id))
        client.send_gmsg("test")

    def on_close(self, client):
        print(f"Client {client.obj_id} disconnected")

    def username_set(self, client):
        print(f"Client {client.obj_id}'s username was set!")

    def on_gmsg(self, client, message, listener):
        print(f"Client {client.obj_id} got gmsg {message['val']}")


if __name__ == "__main__":
    # Initialize Cloudlink. You will only need to initialize one instance of the main cloudlink module.
    cl = cloudlink()

    # Create examples for various ways to extend the functionality of Cloudlink Server.
    example = example_events()

    # Example - Multiple clients.
    multi_client = cl.multi_client(async_client=False, logs=True)

    # Spawns 5 clients.
    for x in range(5):
        # Create a new client object. This supports initializing many clients at once.
        client = multi_client.spawn(x, "ws://127.0.0.1:3000/")

        # Binding events - This example binds functions to certain events

        # When a client connects, all functions bound to this event will fire.
        client.bind_event(
            client.events.on_connect,
            example.on_connect
        )

        # When a client disconnects, all functions bound to this event will fire.
        client.bind_event(
            client.events.on_close,
            example.on_close
        )

        # When a client disconnects, all functions bound to this event will fire.
        client.bind_event(
            client.events.on_username_set,
            example.username_set
        )

        # Binding callbacks for commands - This example binds an event when a gmsg packet is handled.
        client.bind_callback_method(client.cl_methods.gmsg, example.on_gmsg)

    print("Waking up now")
    multi_client.run()
    input("All clients are ready. Press enter to shutdown.")
    multi_client.stop()
    input("All clients have shut down. Press enter to exit.")

    # Example - Singular clients.
    client = cl.client(async_client=False, logs=True)

    # Object IDs - Sets a friendly name to a specific client object.
    client.obj_id = "Test"

    # Binding events - This example binds functions to certain events

    # When a client connects, all functions bound to this event will fire.
    client.bind_event(
        client.events.on_connect,
        example.on_connect
    )

    # When a client disconnects, all functions bound to this event will fire.
    client.bind_event(
        client.events.on_close,
        example.on_close
    )

    # When a client disconnects, all functions bound to this event will fire.
    client.bind_event(
        client.events.on_username_set,
        example.username_set
    )

    # Binding callbacks for commands - This example binds an event when a gmsg packet is handled.
    client.bind_callback_method(client.cl_methods.gmsg, example.on_gmsg)

    # Run the client.
    client.run("ws://127.0.0.1:3000/")
