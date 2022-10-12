from cloudlink import Cloudlink

class customCommands:
    """
    customCommands

    This is an example of Cloudlink's custom commands system. 
    """

    def __init__(self, cloudlink, extra_data:any = None):
        # To use custom commands, you will need to initialize your custom commands class with Cloudlink. This is required.
        self.cloudlink = cloudlink

        # You can specify which functions to ignore when using cloudlink.server.loadCustomCommands. This is optional.
        self.importer_ignore_functions = [] # ["test"] if you don't want to load the custom command "test".

        # You can specify extra data to this class, see __main__ below.
        self.extra_data = extra_data

        # Optionally, you can reference Cloudlink components for extended functionality.
        self.supporter = self.cloudlink.supporter

    async def test(self, client, message, listener_detected, listener_id, room_id):
        """
        To define a custom command, a command must contain the following parameters:
        self, client, server, message, listener_detected, listener_id, room_id

        self - Should be a class reference to itself.
        client - Dictionary object that identifies clients. Contains headers, address, handler, and id. See /cloudlink/websocket_server/websocket_server.py for info.
        message - The command's payload.
        listener_detected - Boolean that is set when cloudlink.server.serverRootHandlers checks a packet and identifies the JSON key "listener" in a packet.
        listener_id - Any value that is set when cloudlink.server.serverRootHandlers checks a packet and reads the JSON key "listener" in a packet.
        room_id - Array of strings that is set when a client has been linked to rooms. Defaults to either None or ["default"].

        You will pass listener_detected, listener_id, and room_id to various cloudlink functions. See cloudlink.server for more info.
        """
        await self.cloudlink.sendPacket(client, {"cmd": "direct", "val": "test"}, listener_detected, listener_id, room_id)

class demoCallbacksServer:
    """
    demoCallbacksServer

    This is an example of Cloudlink's callback system.
    """

    def __init__(self, cloudlink):
        # To use callbacks, you will need to initialize your callbacks class with Cloudlink. This is required.
        self.cloudlink = cloudlink

    async def on_packet(self, client, message):
        print("on_packet fired!")
    
    async def on_connect(self, client):
        print("on_connect fired!")

    async def on_close(self, client):
        print("on_close fired!")
        
    # Below are templates for binding command-specific callbacks. These commands are already handled in the server, but you can extend functionality using this feature.

    async def on_direct(self, message:any, origin:any, listener_detected:bool, listener_id:str): # Called when a packet is handled with the direct command.
        print("on_direct fired!")

    async def on_setid(self, motd:str): # Called when a packet is handled with the setid command.
        print("on_setid fired!")

    async def on_ulist(self, ulist:list): # Called when a packet is handled with the ulist command.
        print("on_ulist fired!")

    async def on_statuscode(self, code:str, message:any): # Called when a packet is handled with the statuscode command.
        print("on_statuscode fired!")
    
    async def on_gmsg(self, message:any): # Called when a packet is handled with the gmsg command.
        print("on_gmsg fired!")

    async def on_gvar(self, var_name:str, var_value:any): # Called when a packet is handled with the gvar command.
        print("on_gvar fired!")

    async def on_pvar(self, var_name:str, var_value:any, origin:any): # Called when a packet is handled with the pvar command.
        print("on_pvar fired!")

    async def on_pmsg(self, value:str, origin:any): # Called when a packet is handled with the pmsg command.
        print("on_pmsg fired!")

    async def on_ping(self, value:str, origin:any): # Called when a ping is handled.
        print("on_ping fired!")

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

    # Bind template callbacks
    #server.callback(server.on_direct, dummy.on_direct)
    server.callback(server.on_ulist, dummy.on_ulist)
    server.callback(server.on_statuscode, dummy.on_statuscode)
    server.callback(server.on_setid, dummy.on_setid)
    server.callback(server.on_gmsg, dummy.on_gmsg)
    server.callback(server.on_gvar, dummy.on_gvar)
    server.callback(server.on_pvar, dummy.on_pvar)
    server.callback(server.on_pmsg, dummy.on_pmsg)
    server.callback(server.on_ping, dummy.on_ping)

    # To pass custom commands, simply pass a list containing uninitialized classes.
    # To specify custom parameters, pass a dictionary object with an uninitialized class as a key and your custom parameters as it's value.
    #client.loadCustomCommands(customCommands, {customCommands: dummy})
    server.loadCustomCommands(customCommands)

    # Command disabler. Simply pass a list of strings containing either CLPv4 commands to ignore, or custom commands to unload.
    #server.disableCommands(["gmsg"])
    
    # Reject mode. You can simply set this boolean to true and Cloudlink will terminate future client connections.
    # This can be toggled on-demand. Simply set to false to allow connections. Defaults to false.
    #server.rejectClientMode = True
    
    # Start the server.
    server.run(host="0.0.0.0", port = 3000)
    input("Press enter to exit.")