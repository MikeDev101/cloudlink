from cloudlink import Cloudlink

class demoCallbacksClient:
    """
    demoCallbacksClient

    This is an example of Cloudlink's callback system.
    """

    def __init__(self, cloudlink):
        # To use callbacks, you will need to initialize your callbacks class with Cloudlink. This is required.
        self.cloudlink = cloudlink

    # Below are templates for binding generic callbacks.
    
    def on_packet(self, message): # Called when any packet is received, regardless of packet command.
        print("on_packet fired!")
    
    def on_connect(self): # Called when the client is connected to the server.
        print("on_connect fired!")
        self.cloudlink.sendGlobalMessage("this is a test")
        self.cloudlink.setUsername("test")

    def on_close(self, close_status_code, close_msg): # Called when the client is disconnected from the server.
        print("on_close fired!")

    def on_error(self, error): # Called when the client encounters an exception.
        print("on_error fired!")

     # Below are templates for binding command-specific callbacks.

    def on_direct(self, message:any): # Called when a packet is received with the direct command.
        print("on_direct fired!")
        #pass

    def on_version(self, version:str): # Called when a packet is received with the server_version command.
        print("on_version fired!")
        # pass

    def on_motd(self, motd:str): # Called when a packet is received with the motd command.
        print("on_motd fired!")
        # pass
    
    def on_ip(self, ip:str): # Called when a packet is received with the client_ip command.
        print("on_ip fired!")
        # pass

    def on_ulist(self, ulist:list): # Called when a packet is received with the ulist command.
        print("on_ulist fired!")
        # pass

    def on_statuscode(self, code:str): # Called when a packet is received with the statuscode command.
        print("on_statuscode fired!")
        # pass
    
    def on_gmsg(self, message:str): # Called when a packet is received with the gmsg command.
        print("on_gmsg fired!")
        # pass

    def on_gvar(self, var_name:str, var_value:any): # Called when a packet is received with the gvar command.
        print("on_gvar fired!")
        # pass

    def on_pvar(self, var_name:str, var_value:any, origin:any): # Called when a packet is received with the pvar command.
        print("on_pvar fired!")
        # pass

    def on_pmsg(self, value:str, origin:any): # Called when a packet is received with the pmsg command.
        print("on_pmsg fired!")
        # pass

    def on_ping(self, value:str, origin:any): # Called when the client is being pinged by another client (It will automatically respond to the ping, this is just used for diagnostics).
        print("on_ping fired!")
        # pass

if __name__ == "__main__":
    # Initialize Cloudlink. You will only need to initialize one instance of the main cloudlink module.
    cl = Cloudlink()

    # Create a new client object. This supports initializing many clients at once.
    client = cl.client(logs=True)

    # Create demo callbacks. You can only initialize callbacks after you have initialized a cloudlink client object.
    dummy = demoCallbacksClient(client)

    # Bind demo callbacks
    client.callback(client.on_packet, dummy.on_packet)
    client.callback(client.on_connect, dummy.on_connect)
    client.callback(client.on_close, dummy.on_close)
    client.callback(client.on_error, dummy.on_error)

    # Bind template callbacks
    client.callback(client.on_direct, dummy.on_direct)
    client.callback(client.on_version, dummy.on_version)
    client.callback(client.on_motd, dummy.on_motd)
    client.callback(client.on_ip, dummy.on_ip)
    client.callback(client.on_ulist, dummy.on_ulist)
    client.callback(client.on_statuscode, dummy.on_statuscode)
    client.callback(client.on_gmsg, dummy.on_gmsg)
    client.callback(client.on_gvar, dummy.on_gvar)
    client.callback(client.on_pvar, dummy.on_pvar)
    client.callback(client.on_pmsg, dummy.on_pmsg)
    client.callback(client.on_ping, dummy.on_ping)

    # Command disabler. Simply pass a list of strings containing CLPv4 commands to ignore.
    #client.disableCommands(["gmsg"])

    # Connect to the server and run the client.
    client.run(ip="ws://127.0.0.1:3000/")