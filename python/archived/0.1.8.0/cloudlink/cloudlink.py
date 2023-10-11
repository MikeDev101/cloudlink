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
        self.version = "0.1.8.0"

    def server(self, logs=False):
        # Initialize Cloudlink server
        from server import server
        return server(self, logs)

    def client(self, server_ip = "ws://127.0.0.1:3000/", logs=False):
        # TODO
        pass

    def relay(self, server_ip = "ws://127.0.0.1:3000/", relay_ip = "127.0.0.1", relay_port = 3000, logs=False):
        # TODO
        pass

class customCommands:
    """
    customCommands

    This is an example of Cloudlink 4.0's new custom commands system. 
    """

    def __init__(self, cloudlink):
        # To use custom commands, you will need to initialize your custom commands class with Cloudlink. This is required.
        self.cloudlink = cloudlink
        # You can specify which functions to ignore when using Cloudlink.server.loadCustomCommands. This is optional.
        self.importer_ignore_functions = [] # ["test"] if you don't want to load the custom command "test".

        # Optionally, you can reference Cloudlink components for extended functionality.
        self.supporter = self.cloudlink.supporter

    def test(self, client, server, message, listener_detected, listener_id, room_id):
        """
        To define a custom command, a command must contain the following parameters:
        self, client, server, message, listener_detected, listener_id, room_id

        self - Should be a class reference to itself.
        client - Dictionary object that identifies clients. Contains headers, address, handler, and id. See /cloudlink/websocket_server/websocket_server.py for info.
        server - Required for the websocket server and for backward compatibility.
        listener_detected - Boolean that is set when Cloudlink.server.serverRootHandlers checks a packet and identifies the JSON key "listener" in a packet.
        listener_id - Any value that is set when Cloudlink.server.serverRootHandlers checks a packet and reads the JSON key "listener" in a packet.
        room_id - Array of strings that is set when a client has been linked to rooms. Defaults to either None or ["default"].

        Most of the time, you will be passing listener_detected, listener_id, and room_id to various cloudlink functions. You will likely never use server.
        """
        self.cloudlink.sendPacket(client, {"cmd": "direct", "val": "test"}, listener_detected, listener_id, room_id)

class demoCallbacks:
    """
    demoCallbacks

    This is an example of Cloudlink's callback compatibility system, which re-implements callbacks used in older versions of Cloudlink.
    It is not recommended to use this feature in newer implementations as it has been replaced with Cloudlink.server.loadCustomCommands.
    """

    def __init__(self):
        pass

    def on_packet(self, client, server, message):
        #print("on_packet")
        pass
    
    def on_connect(self, client, server):
        #print("on_connect")
        pass

    def on_close(self, client, server):
        #print("on_close")
        pass

if __name__ == "__main__":
    cl = Cloudlink()
    dummy = demoCallbacks()

    server = cl.server(logs=True)
    server.setMOTD(True, "CloudLink 4 Test")

    server.callback(server.on_packet, dummy.on_packet)
    server.callback(server.on_connect, dummy.on_connect)
    server.callback(server.on_close, dummy.on_close)

    server.loadCustomCommands(customCommands)
    #server.disableCommands(["gmsg"])

    server.run(host="0.0.0.0", port=3000)