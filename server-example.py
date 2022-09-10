from cloudlink import Cloudlink

class customCommands:
    """
    customCommands

    This is an example of Cloudlink 4.0's custom commands system. 
    """

    def __init__(self, cloudlink, extra_data:any = None):
        # To use custom commands, you will need to initialize your custom commands class with Cloudlink. This is required.
        self.cloudlink = cloudlink

        # You can specify which functions to ignore when using Cloudlink.server.loadCustomCommands. This is optional.
        self.importer_ignore_functions = [] # ["test"] if you don't want to load the custom command "test".

        # You can specify extra data to this class, see __main__ below.
        self.extra_data = extra_data

        # Optionally, you can reference Cloudlink components for extended functionality.
        self.supporter = self.cloudlink.supporter

    def test(self, client, server, message, listener_detected, listener_id, room_id):
        """
        To define a custom command, a command must contain the following parameters:
        self, client, server, message, listener_detected, listener_id, room_id

        self - Should be a class reference to itself.
        client - Dictionary object that identifies clients. Contains headers, address, handler, and id. See /cloudlink/websocket_server/websocket_server.py for info.
        server - Required for the websocket server and for backward compatibility.
        message - The command's payload.
        listener_detected - Boolean that is set when Cloudlink.server.serverRootHandlers checks a packet and identifies the JSON key "listener" in a packet.
        listener_id - Any value that is set when Cloudlink.server.serverRootHandlers checks a packet and reads the JSON key "listener" in a packet.
        room_id - Array of strings that is set when a client has been linked to rooms. Defaults to either None or ["default"].

        Most of the time, you will be passing listener_detected, listener_id, and room_id to various cloudlink functions. You will likely never use server.
        """
        self.cloudlink.sendPacket(client, {"cmd": "direct", "val": "test"}, listener_detected, listener_id, room_id)

class demoCallbacksServer:
    """
    demoCallbacksServer

    This is an example of Cloudlink's callback system.
    """

    def __init__(self, cloudlink):
        # To use callbacks, you will need to initialize your callbacks class with Cloudlink. This is required.
        self.cloudlink = cloudlink

    def on_packet(self, client, server, message):
        print("on_packet fired!")
    
    def on_connect(self, client, server):
        print("on_connect fired!")

    def on_close(self, client, server):
        print("on_close fired!")

if __name__ == "__main__":
    # Initialize Cloudlink. You will only need to initialize one instance of the main cloudlink module.
    cl = Cloudlink()
    
    # Create a new server object. This supports initializing many server at once.
    server = cl.server(logs=True)

    # Set the server's Message-Of-The-Day.
    server.setMOTD(True, "CloudLink 4 Test")

    # Create demo callbacks. You can only initialize callbacks after you have initialized a cloudlink server object.
    dummy = demoCallbacksServer(server)

    # Bind demo callbacks
    server.callback(server.on_packet, dummy.on_packet)
    server.callback(server.on_connect, dummy.on_connect)
    server.callback(server.on_close, dummy.on_close)

    # To pass custom commands, simply pass a list containing uninitialized classes.
    # To specify custom parameters, pass a dictionary object with an uninitialized class as a key and your custom parameters as it's value.
    #client.loadCustomCommands(customCommands, {customCommands: dummy})
    server.loadCustomCommands(customCommands)

    # Command disabler. Simply pass a list of strings containing either CLPv4 commands to ignore, or custom commands to unload.
    #server.disableCommands(["gmsg"])

    server.run(host="0.0.0.0", port=3000)