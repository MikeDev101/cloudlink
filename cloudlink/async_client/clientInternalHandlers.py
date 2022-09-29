class clientInternalHandlers():
    """
    The clientInternalHandlers inter class serves as the clients's built-in command handler.
    These commands are hard-coded per-spec as outlined in the CLPv4 (Cloudlink Protocol) guideline.
    """
    
    def __init__(self, cloudlink):
        self.cloudlink = cloudlink
        self.supporter = self.cloudlink.supporter
        self.importer_ignore_functions = ["relay"]
    
    async def direct(self, message):
        self.supporter.log(f"Client received direct data: \"{message['val']}\"")

        # Fire callbacks
        if self.direct in self.cloudlink.usercallbacks:
            if self.cloudlink.usercallbacks[self.direct] != None:
                
                origin = None
                if "origin" in message:
                    origin = message["origin"]
                
                if "listener" in message:
                    await self.cloudlink.usercallbacks[self.direct](value = message["val"], origin = origin, listener_detected = True, listener_id = message["listener"])
                else:
                    await self.cloudlink.usercallbacks[self.direct](value = message["val"], origin = origin, listener_detected = False, listener_id = None)
    
    async def server_version(self, message):
        self.supporter.log(f"Server reports version: {message['val']}")
        self.cloudlink.sever_version = message['val']

        # Fire callbacks
        if self.server_version in self.cloudlink.usercallbacks:
            if self.cloudlink.usercallbacks[self.server_version] != None:
                await self.cloudlink.usercallbacks[self.server_version](message['val'])
    
    async def motd(self, message):
        self.supporter.log(f"Message of the day: \"{message['val']}\"")
        self.cloudlink.motd_msg = message['val']
        
        # Fire callbacks
        if self.motd in self.cloudlink.usercallbacks:
            if self.cloudlink.usercallbacks[self.motd] != None:
                await self.cloudlink.usercallbacks[self.motd](message['val'])
    
    async def client_ip(self, message):
        self.supporter.log(f"Server reports client IP: {message['val']}")
        self.cloudlink.ip_address = message['val']

        # Fire callbacks
        if self.client_ip in self.cloudlink.usercallbacks:
            if self.cloudlink.usercallbacks[self.client_ip] != None:
                await self.cloudlink.usercallbacks[self.client_ip](message["val"])
    
    async def ulist(self, message):
        self.supporter.log(f"Userlist updated: {message['val']}")

        # Reset the userlist
        if "default" in self.cloudlink.userlist:
            self.cloudlink.userlist = {}
        
        # Update individual values
        if "room" in message:
            self.cloudlink.userlist[message['room']] = message['val']
        else:
            self.cloudlink.userlist["default"] = message['val']

        # Fire callbacks
        if self.ulist in self.cloudlink.usercallbacks:
            if self.cloudlink.usercallbacks[self.ulist] != None:
                await self.cloudlink.usercallbacks[self.ulist](self.cloudlink.userlist)
    
    # Status codes
    async def statuscode(self, message):
        if "listener" in message:
            self.supporter.log(f"Client received status code for handler {message['listener']}: {message['code']}")

            # Check if the username was set
            if (message["listener"] == "username_set") and (message["code"] == self.supporter.codes["OK"]):
                self.cloudlink.myClientObject = message["val"]
                self.supporter.log(f"Client received it's user object: {self.cloudlink.myClientObject}")

            # Check if a ping was successful
            if (message["listener"] == "ping_handler") and (message["code"] == self.supporter.codes["OK"]):
                self.supporter.log("Last automatic ping return was successful!")

        else:
            self.supporter.log(f"Client received status code: {message['code']}")

        # Fire callbacks
        if self.statuscode in self.cloudlink.usercallbacks:
            if self.cloudlink.usercallbacks[self.statuscode] != None:
                await self.cloudlink.usercallbacks[self.statuscode](message["code"], message)
    
    # Global messages
    async def gmsg(self, message):
        self.supporter.log(f"Client received global message with data \"{message['val']}\"")

        # Fire callbacks
        if self.gmsg in self.cloudlink.usercallbacks:
            if self.cloudlink.usercallbacks[self.gmsg] != None:
                await self.cloudlink.usercallbacks[self.gmsg](message["val"])

    # Global cloud variables
    async def gvar(self, message):
        self.supporter.log(f"Client received global variable with data \"{message['val']}\"")

        # Fire callbacks
        if self.gvar in self.cloudlink.usercallbacks:
            if self.cloudlink.usercallbacks[self.gvar] != None:
                await self.cloudlink.usercallbacks[self.gvar](var_name=message["name"], var_value=message["val"])
    
    # Private cloud variables
    async def pvar(self, message):
        self.supporter.log(f"Client received private message with data \"{message['val']}\"")

        # Fire callbacks
        if self.pvar in self.cloudlink.usercallbacks:
            if self.cloudlink.usercallbacks[self.pvar] != None:
                await self.cloudlink.usercallbacks[self.pvar](var_name=message["name"], var_value=message["val"], origin=message["origin"])
    
    # Private messages
    async def pmsg(self, message):
        self.supporter.log(f"Client received private message with data \"{message['val']}\"")

        # Fire callbacks
        if self.pmsg in self.cloudlink.usercallbacks:
            if self.cloudlink.usercallbacks[self.pmsg] != None:
                await self.cloudlink.usercallbacks[self.pmsg](value=message["val"], origin=message["origin"])

    # Pings
    async def ping(self, message):
        self.supporter.log(f"Client received a ping from {message['origin']}!")
        await self.cloudlink.sendPacket({"cmd": "statuscode", "val": self.supporter.codes["OK"], "id": message["origin"], "listener": "ping_handler"})

        # Fire callbacks
        if self.ping in self.cloudlink.usercallbacks:
            if self.cloudlink.usercallbacks[self.ping] != None:
                await self.cloudlink.usercallbacks[self.ping](value=message["val"], origin=message["origin"])

    # WIP
    async def relay(self, message):
        pass