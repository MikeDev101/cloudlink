class serverRootHandlers:
    """
    The serverRootHandlers inter class is an interface for the WebsocketServer to communicate with Cloudlink.
    Cloudlink.serverRootHandlers.onPacket talks to the Cloudlink.packetHandler function to handle packets,
    which will call upon Cloudlink.internalHandlers or some other external, custom code (if used).
    """
    
    def __init__(self, cloudlink):
        self.cloudlink = cloudlink
        self.supporter = self.cloudlink.supporter
    
    def on_connect(self, client, server):
        if not(client == None):
            if self.cloudlink.rejectClientMode:
                self.supporter.log(f"Client {client.id} ({client.full_ip}) was rejected.")

                # Reject the client
                self.supporter.rejectClient(client, "Connection rejected")

            elif client.friendly_ip in self.cloudlink.ipblocklist:
                self.supporter.log(f"Client {client.id} ({client.full_ip}) was blocked from connecting.")

                # Block the client
                self.supporter.rejectClient(client, "IP blocked")
            else:
                self.supporter.log(f"Client {client.id} ({client.full_ip}) connected.")

                # Create attributes for the client
                self.supporter.createAttrForClient(client)

                # Join default room
                self.supporter.linkClientToRooms(client, "default")

                # Report to the client it's IP address
                self.cloudlink.sendPacket(client, {"cmd": "client_ip", "val": str(client.full_ip)}, ignore_rooms = True)

                # Report to the client the CL Server version
                self.cloudlink.sendPacket(client, {"cmd": "server_version", "val": str(self.cloudlink.version)}, ignore_rooms = True)

                # Report to the client the currently cached global message
                self.cloudlink.sendPacket(client, {"cmd": "gmsg", "val": self.cloudlink.global_msg}, ignore_rooms = True)

                # Update the client's userlist
                self.cloudlink.sendPacket(client, {"cmd": "ulist", "val": self.supporter.getUsernames()}, ignore_rooms = True)

                # Tell the client the server's Message-Of-The-Day (MOTD)
                if self.cloudlink.motd_enable:
                    self.cloudlink.sendPacket(client, {"cmd": "motd", "val": self.cloudlink.motd_msg}, ignore_rooms = True)

                if self.on_connect in self.cloudlink.usercallbacks:
                    if self.cloudlink.usercallbacks[self.on_connect] != None:
                        self.cloudlink.usercallbacks[self.on_connect](client=client, server=server)
    
    def on_close(self, client, server):
        if not(client == None):
            self.supporter.log(f"Client {client.id} ({client.full_ip}) disconnected.")
            
            # Remove client from all rooms (Required to prevent BrokenPipeErrors)
            self.supporter.removeClientFromAllRooms(client)

            # Update ulists in all rooms
            for room in self.cloudlink.roomData:
                clist = self.cloudlink.getAllUsersInRoom(room)
                ulist = self.supporter.getUsernames(room)
                self.supporter.sendPacket(clist, {"cmd": "ulist", "val": ulist}, rooms = room)

            if self.on_close in self.cloudlink.usercallbacks:
                if self.cloudlink.usercallbacks[self.on_close] != None:
                    self.cloudlink.usercallbacks[self.on_close](client=client, server=server)
    
    def on_packet(self, client, server, message):
        if not(client == None):
            if len(message) == 0:
                self.supporter.log(f"Packet from {client.id} was blank!")
                self.cloudlink.sendCode(client, "EmptyPacket")
            else:
                try:
                    isPacketSane = self.supporter.isPacketSane(message)
                    if isPacketSane:
                        message = self.supporter.json.loads(message)
                    
                        # Convert keys in the packet to proper JSON (Primarily for Scratch-based clients)
                        for key in message.keys():
                            if type(message[key]) == str:
                                if self.supporter.isJSON(message[key]):
                                    message[key] = self.supporter.json.loads(message[key])
        
                        # Check if the packet contains a listener ID
                        listener_detected = ("listener" in message)
                        listener_id = None
                        if listener_detected:
                            listener_id = message["listener"]
                        else:
                            # Check for old layout (Mainly for Direct command) listeners
                            if type(message["val"]) == str:
                                listener_detected = ("listener" in message["val"])
                                if listener_detected:
                                    listener_id = message["val"]["listener"]
                
                        room_id = None
                        if client.is_linked:
                            room_id = client.rooms

                        if "rooms" in message:
                            if type(message["rooms"]) in [str, list]:
                                # Convert to set
                                if type(message["rooms"]) == str:
                                    message["rooms"] = set([message["rooms"]])
                                elif type(message["rooms"]) == list:
                                    message["rooms"] = set(message["rooms"])
                                room_id = message["rooms"]
                            
                            # Remove unlinked rooms
                            tmp_room_id = room_id.copy()
                            for room in tmp_room_id:
                                if not room in client.rooms:
                                    self.supporter.log(f"Client {client.id} ({client.full_ip}) attempted to access room {room}, but was blocked!")
                                    room_id.remove(room)

                        # Check if the command is a built-in Cloudlink command
                        if ((message["cmd"] in self.cloudlink.builtInCommands) and not(message["cmd"] == "direct")):
                            getattr(self.cloudlink, str(message["cmd"]))(client, server, message, listener_detected, listener_id, room_id)
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
                                    self.supporter.log(f"Client {client.id} ({client.full_ip}) sent legacy custom command \"{message['val']['cmd']}\"")
                                    getattr(self.cloudlink, str(message["val"]["cmd"]))(client, server, message, listener_detected, listener_id, room_id)
                                else:
                                    if isCustom:
                                        self.supporter.log(f"Client {client.id} ({client.full_ip}) sent custom command \"{message['cmd']}\"")
                                        getattr(self.cloudlink, str(message["cmd"]))(client, server, message, listener_detected, listener_id, room_id)
                                    else:
                                        getattr(self.cloudlink, "direct")(client, server, message, listener_detected, listener_id, room_id)
                            else:
                                if message["cmd"] in self.cloudlink.disabledCommands:
                                    self.supporter.log(f"Client {client.id} ({client.full_ip}) sent custom command \"{message['cmd']}\", but the command is disabled.")
                                    self.cloudlink.sendCode(client, "Disabled")
                                else:
                                    self.supporter.log(f"Client {client.id} ({client.full_ip}) sent custom command \"{message['cmd']}\", but the command is invalid or it was not loaded.")
                                    self.cloudlink.sendCode(client, "Invalid")

                        if self.on_packet in self.cloudlink.usercallbacks:
                            if self.cloudlink.usercallbacks[self.on_packet] != None:
                                self.cloudlink.usercallbacks[self.on_packet](client=client, server=server, message=message)
                    else:
                        self.supporter.log(f"Packet \"{message}\" is invalid, incomplete, or malformed!")
                        self.cloudlink.sendCode(client, "Syntax")
                except:
                    self.supporter.log(f"An exception has occurred. {self.supporter.full_stack()}")
                    self.cloudlink.sendCode(client, "InternalServerError")