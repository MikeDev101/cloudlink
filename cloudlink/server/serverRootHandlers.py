import copy

class serverRootHandlers:
    """
    The serverRootHandlers inter class is an interface for the WebsocketServer to communicate with Cloudlink.
    cloudlink.serverRootHandlers.on_packet talks to cloudlink.serverInternalHandlers or some other external, custom code (if used).
    """
    
    def __init__(self, cloudlink):
        self.cloudlink = cloudlink
        self.supporter = self.cloudlink.supporter
    
    async def on_connect(self, client):
        if client == None:
            return
        
        if self.cloudlink.rejectClientMode:
            self.supporter.log(f"Client {client.id} ({client.full_ip}) was rejected.")

            # Reject the client
            await self.cloudlink.rejectClient(client, "Connection rejected")

        elif client.full_ip in self.cloudlink.ipblocklist:
            self.supporter.log(f"Client {client.id} ({client.full_ip}) was blocked from connecting.")

            # Block the client
            await self.cloudlink.rejectClient(client, "IP blocked")
        else:
            self.supporter.log(f"Client {client.id} ({client.full_ip}) connected.")
            
            # Join default room
            self.cloudlink.linkClientToRooms(client, "default")

            # Report to the client it's IP address
            await self.cloudlink.sendPacket(client, {"cmd": "client_ip", "val": str(client.full_ip)}, ignore_rooms = True)

            # Report to the client the CL Server version
            await self.cloudlink.sendPacket(client, {"cmd": "server_version", "val": str(self.cloudlink.version)}, ignore_rooms = True)

            # Report to the client the currently cached global message
            await self.cloudlink.sendPacket(client, {"cmd": "gmsg", "val": self.cloudlink.global_msg}, ignore_rooms = True)

            # Update the client's userlist
            pages, size, ulist = self.supporter.paginate_ulist(self.cloudlink.getUsernames())
            await self.cloudlink.sendPacket(client, {"cmd": "ulist", "pages": pages, "size": size, "val": ulist}, ignore_rooms = True)

            # Tell the client the server's Message-Of-The-Day (MOTD)
            if self.cloudlink.motd_enable:
                await self.cloudlink.sendPacket(client, {"cmd": "motd", "val": self.cloudlink.motd_msg}, ignore_rooms = True)

            # Fire callbacks
            if self.on_connect in self.cloudlink.usercallbacks:
                if self.cloudlink.usercallbacks[self.on_connect] != None:
                    await self.cloudlink.usercallbacks[self.on_connect](client=client)
    
    async def on_close(self, client, code, reason):
        if client == None:
            return
        
        self.supporter.log(f"Client {client.id} ({client.full_ip}) disconnected with code {code} and reason \"{reason}\"")
        
        # Remove client from all rooms (Required to prevent BrokenPipeErrors)
        self.cloudlink.removeClientFromAllRooms(client)

        # Update ulists in all rooms
        tmp_roomData = copy.copy(self.cloudlink.roomData)
        for room in tmp_roomData:
            clist = self.cloudlink.getAllUsersInRoom(room)
            pages, size, ulist = self.supporter.paginate_ulist(self.cloudlink.getUsernames(room))
            await self.cloudlink.sendPacket(clist, {"cmd": "ulist", "pages": pages, "size": size, "val": ulist}, rooms = room)

        # Fire callbacks
        if self.on_close in self.cloudlink.usercallbacks:
            if self.cloudlink.usercallbacks[self.on_close] != None:
                await self.cloudlink.usercallbacks[self.on_close](client=client)
    
    async def on_packet(self, client, message):
        if client == None:
            return
        
        if client.rejected:
            return
        
        if len(message) == 0:
            self.supporter.log(f"Packet from {client.id} was blank!")
            await self.cloudlink.sendCode(client, "EmptyPacket")
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
                        await getattr(self.cloudlink, str(message["cmd"]))(client, message, listener_detected, listener_id, room_id)
                        # Fire callbacks
                        if self.on_packet in self.cloudlink.usercallbacks:
                            if self.cloudlink.usercallbacks[self.on_packet] != None:
                                await self.cloudlink.usercallbacks[self.on_packet](client=client, message=message)
                    else:
                        # Attempt to read the command as a direct or custom command
                        isCustom = False
                        isLegacy = False
                        isValid = True
                        if message["cmd"] in self.cloudlink.customCommands:
                            # New custom command system.
                            isCustom = True
                            
                            # Handle command overrides, check if it's a legacy command
                            if type(message["val"]) == dict:
                                if "cmd" in message["val"]:
                                    if message["val"]["cmd"] in self.cloudlink.customCommands:
                                        # Legacy custom command system (using direct)
                                        isLegacy = True
                                    else:
                                        isCustom = True
                            
                        elif message["cmd"] == "direct":
                            if self.supporter.isPacketSane(message["val"]):
                                if type(message["val"]) == dict:
                                    if "cmd" in message["val"]:
                                        if message["val"]["cmd"] in self.cloudlink.customCommands:
                                            # Legacy custom command system (using direct)
                                            isLegacy = True
                                    else:
                                        isCustom = True
                                else:
                                    isCustom = True
                        else:
                            isValid = False
                        
                        if isValid:
                            if isLegacy:
                                self.supporter.log(f"Client {client.id} ({client.full_ip}) sent legacy custom command \"{message['val']['cmd']}\"")
                                await getattr(self.cloudlink, str(message["val"]["cmd"]))(client, message["val"], listener_detected, listener_id, room_id)
                            else:
                                if isCustom:
                                    self.supporter.log(f"Client {client.id} ({client.full_ip}) sent custom command \"{message['cmd']}\"")
                                    await getattr(self.cloudlink, str(message["cmd"]))(client, message, listener_detected, listener_id, room_id)
                                else:
                                    await getattr(self.cloudlink, "direct")(client, message, listener_detected, listener_id, room_id)
                            
                            # Fire callbacks
                            if self.on_packet in self.cloudlink.usercallbacks:
                                if self.cloudlink.usercallbacks[self.on_packet] != None:
                                    await self.cloudlink.usercallbacks[self.on_packet](client=client, message=message)
                        else:
                            if message["cmd"] in self.cloudlink.disabledCommands:
                                self.supporter.log(f"Client {client.id} ({client.full_ip}) sent custom command \"{message['cmd']}\", but the command is disabled.")
                                await self.cloudlink.sendCode(client, "Disabled", listener_detected, listener_id)
                            else:
                                self.supporter.log(f"Client {client.id} ({client.full_ip}) sent custom command \"{message['cmd']}\", but the command is invalid or it was not loaded.")
                                await self.cloudlink.sendCode(client, "Invalid", listener_detected, listener_id)
                                
                else:
                    self.supporter.log(f"Packet \"{message}\" is invalid, incomplete, or malformed!")
                    await self.cloudlink.sendCode(client, "Syntax")
            except:
                self.supporter.log(f"An exception has occurred. {self.supporter.full_stack()}")
                await self.cloudlink.sendCode(client, "InternalServerError")