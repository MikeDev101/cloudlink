from .cloudlink import cloudlink


class example_events:
    def __init__(self):
        pass

    async def on_close(self, client):
        print("Client", client.id, "disconnected.")

    async def on_connect(self, client):
        print("Client", client.id, "connected.")


if __name__ == "__main__":
    cl = cloudlink()
    server = cl.server(logs=True)
    events = example_events()
    server.set_motd("CL4 Demo Server", True)
    server.bind_event(server.events.on_connect, events.on_connect)
    server.bind_event(server.events.on_close, events.on_close)
    print("Welcome to Cloudlink 4! See https://github.com/mikedev101/cloudlink for more info. Now running server on ws://127.0.0.1:3000/!")
    server.run(ip="localhost", port=3000)