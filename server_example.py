from cloudlink import cloudlink

class example_callbacks:
    def __init__(self, cloudlink):
        self.cloudlink = cloudlink

        # If you want to have commands with very specific formatting, use the validate() function.
        self.validate = cloudlink.validate

        # Various ways to send messages
        self.send_packet_unicast = cloudlink.send_packet_unicast
        self.send_packet_multicast = cloudlink.send_packet_multicast
        self.send_packet_multicast_variable = cloudlink.send_packet_multicast_variable
        self.send_code = cloudlink.send_code
    
    async def test1(self, client, message, listener_detected, listener_id):
        #print("Test1!")
        #await self.cloudlink.asyncio.sleep(1)
        #print("Test1 after one second!")
        pass
    
    async def test2(self, client, message, listener_detected, listener_id):
        #print("Test2!")
        #await self.cloudlink.asyncio.sleep(1)
        #print("Test2 after one second!")
        pass
    
    async def test3(self, client, message, listener_detected, listener_id):
        #print("Test3!")
        pass

class example_commands:
    def __init__(self, cloudlink):
        self.cloudlink = cloudlink

        # If you want to have commands with very specific formatting, use the validate() function.
        self.validate = cloudlink.validate

        # Various ways to send messages
        self.send_packet_unicast = cloudlink.send_packet_unicast
        self.send_packet_multicast = cloudlink.send_packet_multicast
        self.send_packet_multicast_variable = cloudlink.send_packet_multicast_variable
        self.send_code = cloudlink.send_code
    
    async def foobar(self, client, message, listener_detected, listener_id):
        print("Foobar!")

if __name__ == "__main__":
    # Initialize Cloudlink. You will only need to initialize one instance of the main cloudlink module.
    cl = cloudlink()

    # Create a new server object. This supports initializing many servers at once.
    server = cl.server(logs = True)

    test1 = example_callbacks(server)
    test2 = example_commands(server)

    # Extra configuration
    server.enable_motd = True # Defaulted to False
    server.motd_message = "CL4 Optimized! Gotta Go Fast!" # Defaulted to empty string
    #server.ip_blocklist = ["127.0.0.1"] # Defaulted to empty list
    #server.reject_clients = False # Defaulted to False
    #server.check_ip_addresses = True # Defaulted to False
    
    # Binding callbacks - This example binds the "handshake" command with example callbacks.
    # You can bind as many callbacks as you want to a function, however they must use async.
    server.bind_callback(server.cl_methods.handshake, test1.test1)
    server.bind_callback(server.cl_methods.handshake, test1.test2)
    
    # Creating custom commands - This example adds a custom command "foobar" from example_commands
    # and then binds the callback test3 to the new command.
    server.load_custom_methods(test2)
    server.bind_callback(test2.foobar, test1.test3)
    
    server.run(ip = "localhost", port = 3000)