from .supporter import supporter

# Hippity hoppity, better peformance is now on your property
import websockets as async_websockets
import asyncio

# If you need it, you can use the non-Async client.
import websocket as old_websockets

"""
CloudLink 4.0 Server and Client

CloudLink is a free and open-source, websocket-powered API optimized for Scratch 3.0.
For documentation, please visit https://hackmd.io/g6BogABhT6ux1GA2oqaOXA

Cloudlink is built upon https://github.com/aaugustin/websockets.

Please see https://github.com/MikeDev101/cloudlink for more details.

Cloudlinks's dependencies are:
* websockets

These dependencies are built-in to Python.
* threading
* asyncio
* traceback
* datetime
* json
"""

class Cloudlink:
    def __init__(self):
        self.version = "0.1.8.7"
        self.supporter = supporter
        print(f"Cloudlink v{self.version}")

    def server(self, logs:bool = False):
        # Initialize Cloudlink server
        self.ws = async_websockets
        self.asyncio = asyncio
        from .server import server
        return server(self, logs)

    def client(self, logs:bool = False, async_client:bool = True):
        # Initialize Cloudlink client
        if async_client:
            self.ws = async_websockets
            self.asyncio = asyncio
            from .async_client import client
        else:
            self.ws = old_websockets
            from .old_client import client
        return client(self, logs)

    def relay(self, logs:bool = False):
        # TODO: Client and server modes now exist together, still need to finish spec and functionality for Relay mode
        pass
