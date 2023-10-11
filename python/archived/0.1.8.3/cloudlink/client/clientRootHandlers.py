class clientRootHandlers:
    """
    The clientRootHandlers inter class is an interface for the WebsocketClient to communicate with Cloudlink.
    Cloudlink.clientRootHandlers.onPacket talks to the Cloudlink.packetHandler function to handle packets,
    which will call upon Cloudlink.internalHandlers or some other external, custom code (if used).
    """
    
    def __init__(self, cloudlink):
        self.cloudlink = cloudlink
        self.supporter = self.cloudlink.supporter
    
    def on_error(self, ws, error):
        if not error == None:
            return
        self.supporter.log(f"Client error: {error}")

        # Fire callbacks
        if self.on_error in self.cloudlink.usercallbacks:
            if self.cloudlink.usercallbacks[self.on_error] != None:
                self.cloudlink.usercallbacks[self.on_error](error=error)
    
    def on_connect(self, ws):
        self.supporter.log(f"Client connected.")
        self.cloudlink.linkStatus = 2
        self.cloudlink.connected = True

        # Fire callbacks
        if self.on_connect in self.cloudlink.usercallbacks:
            if self.cloudlink.usercallbacks[self.on_connect] != None:
                self.cloudlink.usercallbacks[self.on_connect]()
    
    def on_close(self, ws, close_status_code, close_msg):
        if self.cloudlink.linkStatus == 1:
            self.cloudlink.linkStatus = 4
            self.cloudlink.failedToConnect = True
            self.supporter.log(f"Client failed to connect! Disconnected with status code {close_status_code} and message \"{close_msg}\"")
        elif self.cloudlink.linkStatus == 2:
            self.cloudlink.linkStatus = 4
            self.cloudlink.connectionLost = True
            self.supporter.log(f"Client lost connection! Disconnected with status code {close_status_code} and message \"{close_msg}\"")
        else:
            self.cloudlink.linkStatus = 3
            self.supporter.log(f"Client gracefully disconnected! Disconnected with status code {close_status_code} and message \"{close_msg}\"")
        self.cloudlink.connected = False

        # Fire callbacks
        if self.on_close in self.cloudlink.usercallbacks:
            if self.cloudlink.usercallbacks[self.on_close] != None:
                self.cloudlink.usercallbacks[self.on_close](close_status_code=close_status_code, close_msg=close_msg)
    
    def on_packet(self, ws, message):
        if len(message) != 0:
            try:
                isPacketSane = self.supporter.isPacketSane(message)
                if isPacketSane:
                    message = self.supporter.json.loads(message)
                
                    # Convert keys in the packet to proper JSON (Primarily for Scratch-based clients)
                    for key in message.keys():
                        if type(message[key]) == str:
                            if self.supporter.isJSON(message[key]):
                                message[key] = self.supporter.json.loads(message[key])

                    # Check if the command is a built-in Cloudlink command
                    if ((message["cmd"] in self.cloudlink.builtInCommands) and not(message["cmd"] == "direct")):
                        getattr(self.cloudlink, str(message["cmd"]))(message)
                        # Fire callbacks
                        if self.on_packet in self.cloudlink.usercallbacks:
                            if self.cloudlink.usercallbacks[self.on_packet] != None:
                                self.cloudlink.usercallbacks[self.on_packet](message=message)
                    else:
                        # Attempt to read the command as a direct or custom command
                        isCustom = False
                        isLegacy = False
                        isValid = True
                        if message["cmd"] in self.cloudlink.customCommands:
                            # New custom command system.
                            isCustom = True
                        elif message["cmd"] == "direct":
                            if self.supporter.isPacketSane(message["val"]):
                                if type(message["val"]) == dict:
                                    if message["val"]["cmd"] in self.cloudlink.customCommands:
                                        # Legacy custom command system (using direct)
                                        isLegacy = True
                                else:
                                    isCustom = True
                        else:
                            isValid = False
                        if isValid:
                            if isLegacy:
                                self.supporter.log(f"Client recieved legacy custom command \"{message['val']['cmd']}\"")
                                getattr(self.cloudlink, str(message["val"]["cmd"]))(message=message)
                            else:
                                if isCustom:
                                    self.supporter.log(f"Client recieved custom command \"{message['cmd']}\"")
                                    getattr(self.cloudlink, str(message["cmd"]))(message=message)
                                else:
                                    getattr(self.cloudlink, "direct")(message=message)
                            
                            # Fire callbacks
                            if self.on_packet in self.cloudlink.usercallbacks:
                                if self.cloudlink.usercallbacks[self.on_packet] != None:
                                    self.cloudlink.usercallbacks[self.on_packet](message=message)
                        else:
                            if message["cmd"] in self.cloudlink.disabledCommands:
                                self.supporter.log(f"Client recieved command \"{message['cmd']}\", but the command is disabled.")
                            else:
                                self.supporter.log(f"Client recieved command \"{message['cmd']}\", but the command is invalid or it was not loaded.")
                else:
                    self.supporter.log(f"Packet \"{message}\" is invalid, incomplete, or malformed!")
            except:
                self.supporter.log(f"An exception has occurred. {self.supporter.full_stack()}")