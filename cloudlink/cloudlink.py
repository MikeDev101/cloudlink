#!/usr/bin/env python3

from .supporter import supporter

"""
CloudLink 4.0 Server and Client

CloudLink is a free and open-source, websocket-powered API optimized for Scratch 3.0.
For documentation, please visit https://hackmd.io/g6BogABhT6ux1GA2oqaOXA

Server based on https://github.com/Pithikos/python-websocket-server
The WebsocketServer that is bundled with CloudLink is modified to support Cloudflared and fixes an issue with asserting the HTTP websocket upgrade request.

Client based upon https://github.com/websocket-client/websocket-client

Please see https://github.com/MikeDev101/cloudlink for more details.
"""

class Cloudlink:
    def __init__(self):
        self.version = "0.1.8.3"
        self.supporter = supporter
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
