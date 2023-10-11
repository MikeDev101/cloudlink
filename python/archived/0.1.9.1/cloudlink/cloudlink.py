from .supporter import supporter

"""
CloudLink 4.0 Server and Client

CloudLink is a free and open-source, websocket-powered API optimized for Scratch 3.0.
For documentation, please visit https://hackmd.io/g6BogABhT6ux1GA2oqaOXA

Cloudlink is built upon https://github.com/aaugustin/websockets.

Please see https://github.com/MikeDev101/cloudlink for more details.

Cloudlink's dependencies are:
* websockets

These dependencies are built-in to Python.
* copy
* asyncio
* traceback
* datetime
* json
"""


class cloudlink:
    def __init__(self):
        self.version = "0.1.9.1"
        self.supporter = supporter
        print(f"Cloudlink v{self.version}")

    def server(self, logs: bool = False):
        # Initialize Cloudlink server
        from .server import server
        return server(self, logs)

    def client(self, logs: bool = False, async_client: bool = True):
        # Initialize Cloudlink client
        if async_client:
            from .async_client import async_client
            return async_client.client(self, logs)
        else:
            from .old_client import old_client
            return old_client.client(self, logs)

    def multi_client(self, logs: bool = False, async_client: bool = True):
        # Initialize Cloudlink client
        if async_client:
            from .async_client import async_client
            return async_client.multi_client(self, logs)
        else:
            from .old_client import old_client
            return old_client.multi_client(self, logs)

    def relay(self, logs: bool = False):
        # TODO: Client and server modes now exist together, still need to finish spec and functionality for Relay mode
        pass
