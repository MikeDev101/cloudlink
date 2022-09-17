from .supporter import supporter

# Hippity hoppity, better peformance is now on your property
import websockets
import asyncio

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
        self.version = "0.1.8.6"
        self.asyncio = asyncio
        self.supporter = supporter
        self.ws = websockets
        print(f"Cloudlink v{self.version}")

    def server(self, logs=False):
        # Initialize Cloudlink server
        from .server import server
        return server(self, logs)

    def client(self, logs=False):
        # Initialize Cloudlink client
        from .client import client
        return client(self, logs)

    def relay(self, logs=False):
        # TODO: Client and server modes now exist together, still need to finish spec and functionality for Relay mode
        pass
