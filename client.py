
from cloudlink.client.schema import schema


schema.mycommand = {
    "cmd": {
        "type": "string",
        "required": True
    },
    "val": {
        "type": [
            "string",
            "integer",
            "float",
            "number",
            "boolean",
            "dict",
            "list",
            "set",
        ],
        "required": False,
    },
}

from cloudlink import client
from cloudlink.client import plugin, event, command

class myplugin(plugin):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.parent.logging.debug("myplugin.__init__")

    @event("message")
    async def mycommand(self, data):
        print(f"mycommand: {data}")


if __name__ == "__main__":
    # Initialize the client
    client = client()
    
    # Configure logging settings
    client.logging.basicConfig(
        level=client.logging.DEBUG
    )
    client.suppress_websocket_logs = True

    # Example of events
    @client.on_connect
    async def on_connect():
        print("Connected")
        await client.execute_send({
            "cmd": "mycommand",
            "val": "Hello World"
        })
        await client.asyncio.sleep(1)
        print("Going away")
        client.disconnect()

    pl = myplugin(client)
    client.load_plugin(plugin=pl)

    # Start the client
    client.run(host="ws://127.0.0.1:3000/")
