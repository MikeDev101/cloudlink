#!/usr/bin/env python3

"""
CloudLink Server

CloudLink is a free and open-source, websocket-powered API optimized for Scratch 3.0.
For documentation, please visit https://hackmd.io/g6BogABhT6ux1GA2oqaOXA

Server based on https://github.com/Pithikos/python-websocket-server
The WebsocketServer that is bundled with CloudLink is modified to support Cloudflared and fixes an issue with asserting the HTTP websocket upgrade request.

Please see https://github.com/MikeDev101/cloudlink for more details.
"""

class Cloudlink:
    def __init__(self):
        self.version = "0.1.8.1"

    def server(self, logs=False):
        # Initialize Cloudlink server
        from .server import server
        return server(self, logs)

    def client(self, server_ip = "ws://127.0.0.1:3000/", logs=False):
        # TODO
        pass

    def relay(self, server_ip = "ws://127.0.0.1:3000/", relay_ip = "127.0.0.1", relay_port = 3000, logs=False):
        # TODO
        pass