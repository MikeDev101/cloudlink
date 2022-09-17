from copy import copy

class serverInternalHandlers():
    """
    The serverInternalHandlers inter class serves as the server's built-in command handler.
    These commands are hard-coded per-spec as outlined in the CLPv4 (Cloudlink Protocol) guideline.
    """
    
    def __init__(self, cloudlink):
        self.cloudlink = cloudlink
        self.supporter = self.cloudlink.supporter
        self.importer_ignore_functions = ["relay"]
    
    # Manually fetch the userlist
    async def ulist(self, client, message, listener_detected, listener_id, room_id):
        if not type(message["val"]) == int:
            await self.cloudlink.sendCode(client, "DataType", listener_detected, listener_id)
            return
        
        for room in client.rooms:
            pages, size, ulist = self.supporter.paginate_ulist(self.cloudlink.getUsernames(room), page_select = message["val"])
            await self.cloudlink.sendPacket(client, {"cmd": "ulist", "pages": pages, "size": size, "val": ulist}, rooms = room)
        
        # Fire callbacks
        if self.ulist in self.cloudlink.usercallbacks:
            if self.cloudlink.usercallbacks[self.ulist] != None:
                await self.cloudlink.usercallbacks[self.ulist](ulist)

    # Status codes (For client-to-client)
    async def statuscode(self, client, message, listener_detected, listener_id, room_id):
        # Sanity check the message
        for key in ["val", "id"]:
            if not key in message:
                await self.cloudlink.sendCode(client, "Syntax", listener_detected, listener_id)
                return
        
        if type(message["id"]) == list:
            rx_client = self.cloudlink.selectMultiUserObjects(message["id"])
            if not(len(rx_client) == 0):
                # Send the message to all recipient IDs
                self.supporter.log(f"Client {client.id} ({client.full_ip}) is sending a status code to other clients!")
                await self.cloudlink.sendPacket(rx_client, {"cmd": "statuscode", "code": message["val"], "origin": self.cloudlink.getUserObjectFromClientObj(client)})

                # Tell the client that all status codes were successfully sent
                await self.cloudlink.sendCode(client, "OK", listener_detected, listener_id)
            else:
                # Tell the client that the server failed to find a client with those IDs
                await self.cloudlink.sendCode(client, "IDNotFound", listener_detected, listener_id)
        else:
            rx_client = self.cloudlink.getUserObject(message["id"])
            if rx_client == None:
                # Tell the client that the server failed to find a client with that ID
                await self.cloudlink.sendCode(client, "IDNotFound", listener_detected, listener_id)
                return

            if rx_client == LookupError:
                # Tell the client that the server needs the ID to be more specific
                await self.cloudlink.sendCode(client, "IDNotSpecific", listener_detected, listener_id)
                return

            if rx_client == TypeError:
                # Tell the client it sent an unsupported datatype
                await self.cloudlink.sendCode(client, "DataType", listener_detected, listener_id)
                return
            
            # Send the status code to the recipient ID
            self.supporter.log(f"Client {client.id} ({client.full_ip}) is sending a status code to {rx_client.id} ({rx_client.full_ip})!")
            await self.cloudlink.sendPacket(rx_client, {"cmd": "statuscode", "code": message["val"], "origin": self.cloudlink.getUserObjectFromClientObj(client)}, rooms = room_id)

            # Tell the client that the status code was successfully sent
            await self.cloudlink.sendCode(client, "OK", listener_detected, listener_id)
        
        # Fire callbacks
        if self.statuscode in self.cloudlink.usercallbacks:
            if self.cloudlink.usercallbacks[self.statuscode] != None:
                await self.cloudlink.usercallbacks[self.statuscode](message)

    # Ping
    async def ping(self, client, message, listener_detected, listener_id, room_id):
        # Check if the client is pinging the server only
        if not "id" in message:
            self.supporter.log(f"Client {client.id} ({client.full_ip}) pinged the server!")
            await self.cloudlink.sendCode(client, "OK", listener_detected, listener_id)
            return
        
        # Prevent clients without usernames from linking
        if not client.username_set:
            await self.cloudlink.sendCode(client, "IDRequired", listener_detected, listener_id)
            return

        # Sanity check the message
        for key in ["val", "id"]:
            if not key in message:
                await self.cloudlink.sendCode(client, "Syntax", listener_detected, listener_id)
                return

        if type(message["id"]) == list:
            rx_client = self.cloudlink.selectMultiUserObjects(message["id"])
            if not(len(rx_client) == 0):
                # Send the message to all recipient IDs
                self.supporter.log(f"Client {client.id} ({client.full_ip}) is pinging other clients!")
                await self.cloudlink.sendPacket(rx_client, {"cmd": "ping", "val": message["val"], "origin": self.cloudlink.getUserObjectFromClientObj(client)})
                # Assume that each of the client's recipients will respond with a statuscode
            else:
                # Tell the client that the server failed to find a client with those IDs
                await self.cloudlink.sendCode(client, "IDNotFound", listener_detected, listener_id)
        else:
            rx_client = self.cloudlink.getUserObject(message["id"])
            if rx_client == None:
                # Tell the client that the server failed to find a client with that ID
                await self.cloudlink.sendCode(client, "IDNotFound", listener_detected, listener_id)
                return

            if rx_client == LookupError:
                # Tell the client that the server needs the ID to be more specific
                await self.cloudlink.sendCode(client, "IDNotSpecific", listener_detected, listener_id)
                return

            if rx_client == TypeError:
                # Tell the client it sent an unsupported datatype
                await self.cloudlink.sendCode(client, "DataType", listener_detected, listener_id)
                return
            
            self.supporter.log(f"Client {client.id} ({client.full_ip}) is sending a ping to {rx_client.id} ({rx_client.full_ip})!")
            # Send the ping to the recipient ID
            await self.cloudlink.sendPacket(rx_client, {"cmd": "ping", "val": message["val"], "origin": self.cloudlink.getUserObjectFromClientObj(client)}, rooms = room_id)
            # Assume that the client's recipient will respond with a statuscode
        
        # Fire callbacks
        if self.ping in self.cloudlink.usercallbacks:
            if self.cloudlink.usercallbacks[self.ping] != None:
                await self.cloudlink.usercallbacks[self.ping](message)
    
    # Link client to a room/rooms
    async def link(self, client, message, listener_detected, listener_id, room_id):
        self.supporter.log(f"Client {client.id} ({client.full_ip}) is linking to room(s): {message['val']}")

        # Temporarily save the client's old rooms data
        old_rooms = copy(client.rooms)

        # Prevent clients without usernames from linking
        if not client.username_set:
            await self.cloudlink.sendCode(client, "IDRequired", listener_detected, listener_id)
            return
        
        # Sanity check the message
        if not "val" in message:
            await self.cloudlink.sendCode(client, "Syntax", listener_detected, listener_id)
            return
        
        if type(message["val"]) in [list, str]:
            # Convert to set
            if type(message["val"]) == str:
                message["val"] = set([message["val"]])
            elif type(message["val"]) == list:
                message["val"] = set(message["val"])
            
            existing_link = copy(client.is_linked)
            
            # Remove the client from all rooms and set their room to the default room
            self.cloudlink.unlinkClientFromRooms(client)

            # Add client to rooms
            self.cloudlink.linkClientToRooms(client, message["val"])

            # Tell the client that they were linked
            await self.cloudlink.sendCode(client, "OK", listener_detected, listener_id)

            # Update all client ulists for the default room
            if ("default" in old_rooms) and (not "default" in message["val"]):
                pages, size, ulist = self.supporter.paginate_ulist(self.cloudlink.getUsernames("default"))
                await self.cloudlink.sendPacket(self.cloudlink.getAllUsersInRoom("default"), {"cmd": "ulist", "pages": pages, "size": size, "val": ulist})
            
            if not existing_link:
                # Deduplicate rooms
                new_rooms = client.rooms
                for room in copy(new_rooms):
                    if room in old_rooms:
                        new_rooms.remove(room)
            else:
                new_rooms = client.rooms
            
            for room in new_rooms:
                # Update all client ulists in the rooms that the client joined
                await self.cloudlink.sendPacket(self.cloudlink.getAllUsersInRoom(room), {"cmd": "ulist", "val": self.cloudlink.getUsernames(room)}, rooms = room)

        else:
            await self.cloudlink.sendCode(client, "DataType", listener_detected, listener_id)
    
    # Unlink client from all rooms, and then link the client to the default room
    async def unlink(self, client, message, listener_detected, listener_id, room_id):
        self.supporter.log(f"Client {client.id} ({client.full_ip}) unlinking from all rooms")

        # Prevent clients without usernames from using this command
        if not client.username_set:
            await self.cloudlink.sendCode(client, "IDRequired", listener_detected, listener_id)
            return
        
        if client.is_linked:
            # Temporarily save the client's old rooms data
            old_rooms = copy(client.rooms)

            # Remove the client from all rooms and set their room to the default room
            self.cloudlink.unlinkClientFromRooms(client)

            # Add client to rooms
            self.cloudlink.linkClientToRooms(client, "default")
            client.is_linked = False

            # Tell the client that they were unlinked
            await self.cloudlink.sendCode(client, "OK", listener_detected, listener_id)

            # Update all client ulists for the default room
            pages, size, ulist = self.supporter.paginate_ulist(self.cloudlink.getUsernames())
            await self.cloudlink.sendPacket(self.cloudlink.getAllUsersInRoom("default"), {"cmd": "ulist", "pages": pages, "size": size, "val": ulist})
            
            # Deduplicate the default room
            if "default" in old_rooms:
                old_rooms.remove("default")
            
            # Update all client ulists in the room that the client left
            pages, size, ulist = self.supporter.paginate_ulist(self.cloudlink.getUsernames(old_rooms))
            await self.cloudlink.sendPacket(self.cloudlink.getAllUsersInManyRooms(old_rooms), {"cmd": "ulist", "pages": pages, "size": size, "val": ulist}, rooms = old_rooms)
        else:
            self.supporter.log(f"Client {client.id} ({client.full_ip}) was already unlinked!")
            # Tell the client that it was already unlinked
            await self.cloudlink.sendCode(client, "OK", listener_detected, listener_id)

            # Give the client the default room ulist
            await self.cloudlink.sendPacket(client, {"cmd": "ulist", "val": self.cloudlink.getUsernames()})
    
    # Direct messages, this command is pretty obsolete, since custom commands are loaded directly into Cloudlink instead of using direct in CL3. Idfk what this should do.
    async def direct(self, client, message, listener_detected, listener_id, room_id):
        # Prevent clients without usernames from using this command
        if not client.username_set:
            await self.cloudlink.sendCode(client, "IDRequired", listener_detected, listener_id)
            return
        
        # Sanity check the message, or override it
        if not "id" in message:
            if self.direct in self.cloudlink.usercallbacks:
                self.supporter.log(f"Client {client.id} ({client.full_ip}) sent direct data: \"{message}\"")
                # Fire callbacks
                if self.direct in self.cloudlink.usercallbacks:
                    if self.cloudlink.usercallbacks[self.direct] != None:
                        await self.cloudlink.usercallbacks[self.direct](message = message, origin = self.cloudlink.getUserObject(client), listener_detected = listener_detected, listener_id = listener_id)
            else:
                # Default function of server is to echo the data
                await self.cloudlink.sendPacket(client, {"cmd": "direct", "val": message["val"], "origin": self.cloudlink.getUserObjectFromClientObj(client)}, ignore_rooms = True)
            return
        
        self.supporter.log(f"Client {client.id} ({client.full_ip}) sent direct data: \"{message}\"")

        if type(message["id"]) == list:
            rx_client = self.cloudlink.selectMultiUserObjects(message["id"])
            if not(len(rx_client) == 0):
                # Send the message to all recipient IDs
                self.supporter.log(f"Client {client.id} ({client.full_ip}) is sending direct data to various clients!")
                await self.cloudlink.sendPacket(rx_client, {"cmd": "direct", "val": message["val"], "origin": self.cloudlink.getUserObjectFromClientObj(client)})

                # Tell the client that all direct data were successfully sent
                await self.cloudlink.sendCode(client, "OK", listener_detected, listener_id)
            else:
                # Tell the client that the server failed to find a client with those IDs
                await self.cloudlink.sendCode(client, "IDNotFound", listener_detected, listener_id)
        else:
            rx_client = self.cloudlink.getUserObject(message["id"])
            if rx_client == None:
                # Tell the client that the server failed to find a client with that ID
                await self.cloudlink.sendCode(client, "IDNotFound", listener_detected, listener_id)
                return

            if rx_client == LookupError:
                # Tell the client that the server needs the ID to be more specific
                await self.cloudlink.sendCode(client, "IDNotSpecific", listener_detected, listener_id)
                return

            if rx_client == TypeError:
                # Tell the client it sent an unsupported datatype
                await self.cloudlink.sendCode(client, "DataType", listener_detected, listener_id)
                return

            self.supporter.log(f"Client {client.id} ({client.full_ip}) is sending direct data to {rx_client.id} ({rx_client.full_ip})!")
            # Send the ping to the recipient ID
            await self.cloudlink.sendPacket(rx_client, {"cmd": "direct", "val": message["val"], "origin": self.cloudlink.getUserObjectFromClientObj(client)}, rooms = room_id)

            # Tell the client that the direct data was successfully sent
            await self.cloudlink.sendCode(client, "OK", listener_detected, listener_id)
        
        # Fire callbacks
        if self.direct in self.cloudlink.usercallbacks:
            if self.cloudlink.usercallbacks[self.direct] != None:
                await self.cloudlink.usercallbacks[self.direct](message = message, origin = self.cloudlink.getUserObject(client), listener_detected = listener_detected, listener_id = listener_id)
    
    # Global messages
    async def gmsg(self, client, message, listener_detected, listener_id, room_id):
        self.supporter.log(f"Client {client.id} ({client.full_ip}) sent global message with data \"{message['val']}\"")
        msg = {
            "cmd": "gmsg",
            "val": message["val"]
        }
        
        # Send the message to all clients except the origin
        if room_id in [None, "default"]:
            ulist = self.cloudlink.getAllUsersInRoom("default")
            if client in ulist:
                ulist.remove(client)
            await self.cloudlink.sendPacket(ulist, msg)

            # Cache the last message for new clients
            self.cloudlink.global_msg = message["val"]
        else:
            for room in room_id:
                ulist = []
                for user in self.cloudlink.getAllUsersInRoom(room):
                    ulist.append(user)
                ulist.remove(client)
                await self.cloudlink.sendPacket(ulist, msg, rooms = room)
        
        # Send the message back to origin
        await self.cloudlink.sendPacket(client, msg, listener_detected, listener_id, room_id)
        
        # Fire callbacks
        if self.gmsg in self.cloudlink.usercallbacks:
            if self.cloudlink.usercallbacks[self.gmsg] != None:
                await self.cloudlink.usercallbacks[self.gmsg](message)

    # Global cloud variables
    async def gvar(self, client, message, listener_detected, listener_id, room_id):
        # Sanity check the message
        for key in ["val", "name"]:
            if not key in message:
                await self.cloudlink.sendCode(client, "Syntax", listener_detected, listener_id)
                return

        self.supporter.log(f"Client {client.id} ({client.full_ip}) sent global variable with data \"{message['val']}\"")
        
        msg = {
            "cmd": "gvar",
            "val": message["val"],
            "name": message["name"]
        }
        
        # Send the message to all clients except the origin
        if room_id in [None, "default"]:
            ulist = self.cloudlink.getAllUsersInRoom("default")
            if client in ulist:
                ulist.remove(client)
            await self.cloudlink.sendPacket(ulist, msg)

            # Cache the last message for new clients
            self.cloudlink.global_msg = message["val"]
        else:
            for room in room_id:
                ulist = []
                for user in self.cloudlink.getAllUsersInRoom(room):
                    ulist.append(user)
                ulist.remove(client)
                await self.cloudlink.sendPacket(ulist, msg, rooms = room)
            
        # Send the message back to origin
        await self.cloudlink.sendPacket(client, msg, listener_detected, listener_id, room_id)
        
        # Fire callbacks
        if self.gvar in self.cloudlink.usercallbacks:
            if self.cloudlink.usercallbacks[self.gvar] != None:
                await self.cloudlink.usercallbacks[self.gvar](var_value = message["val"], var_name = message["name"])
    
    # Private cloud variables
    async def pvar(self, client, message, listener_detected, listener_id, room_id):
        # Prevent clients without usernames from using this command
        if not client.username_set:
            await self.cloudlink.sendCode(client, "IDRequired", listener_detected, listener_id)
            return
        
        # Sanity check the message
        for key in ["val", "name", "id"]:
            if not key in message:
                await self.cloudlink.sendCode(client, "Syntax", listener_detected, listener_id)
                return
        
        if type(message["id"]) == list:
            rx_client = self.cloudlink.selectMultiUserObjects(message["id"])
            if not(len(rx_client) == 0):
                # Send the message to all recipient IDs
                self.supporter.log(f"Client {client.id} ({client.full_ip}) sent private variable data \"{message['val']}\" going to various clients!")
                await self.cloudlink.sendPacket(rx_client, {"cmd": "pvar", "val": message["val"], "name": message["name"], "origin": self.cloudlink.getUserObjectFromClientObj(client)}, rooms = room_id)

                # Tell the client that the messages were successfully sent
                await self.cloudlink.sendCode(client, "OK", listener_detected, listener_id)
            else:
                # Tell the client that the server failed to find a client with those IDs
                await self.cloudlink.sendCode(client, "IDNotFound", listener_detected, listener_id)
        else:
            rx_client = self.cloudlink.getUserObject(message["id"])
            if rx_client == None:
                # Tell the client that the server failed to find a client with that ID
                await self.cloudlink.sendCode(client, "IDNotFound", listener_detected, listener_id)
                return

            if rx_client == LookupError:
                # Tell the client that the server needs the ID to be more specific
                await self.cloudlink.sendCode(client, "IDNotSpecific", listener_detected, listener_id)
                return

            if rx_client == TypeError:
                # Tell the client it sent an unsupported datatype
                await self.cloudlink.sendCode(client, "DataType", listener_detected, listener_id)
                return

            # Send the message to the recipient ID
            self.supporter.log(f"Client {client.id} ({client.full_ip}) sent private variable data \"{message['val']}\" going to {rx_client.id} ({rx_client.full_ip})!")
            await self.cloudlink.sendPacket(rx_client, {"cmd": "pvar", "val": message["val"], "name": message["name"], "origin": self.cloudlink.getUserObjectFromClientObj(client)}, rooms = room_id)

            # Tell the client that the message was successfully sent
            await self.cloudlink.sendCode(client, "OK", listener_detected, listener_id)
        
        # Fire callbacks
        if self.pvar in self.cloudlink.usercallbacks:
            if self.cloudlink.usercallbacks[self.pvar] != None:
                await self.cloudlink.usercallbacks[self.pvar](var_value = message["val"], var_name = message["name"], origin = self.cloudlink.getUserObject(client))
    
    # Private messages
    async def pmsg(self, client, message, listener_detected, listener_id, room_id):
        # Prevent clients without usernames from using this command
        if not client.username_set:
            await self.cloudlink.sendCode(client, "IDRequired", listener_detected, listener_id)
            return

        # Sanity check the message
        for key in ["val", "id"]:
            if not key in message:
                await self.cloudlink.sendCode(client, "Syntax", listener_detected, listener_id)
                return
        
        if type(message["id"]) == list:
            rx_client = self.cloudlink.selectMultiUserObjects(message["id"])
            if not(len(rx_client) == 0):
                # Send the message to all recipient IDs
                self.supporter.log(f"Client {client.id} ({client.full_ip}) sent private messsage data \"{message['val']}\" going to various clients!")
                await self.cloudlink.sendPacket(rx_client, {"cmd": "pmsg", "val": message["val"], "origin": self.cloudlink.getUserObjectFromClientObj(client)})

                # Tell the client that the messages were successfully sent
                await self.cloudlink.sendCode(client, "OK", listener_detected, listener_id)
            else:
                # Tell the client that the server failed to find a client with those IDs
                await self.cloudlink.sendCode(client, "IDNotFound", listener_detected, listener_id)
        else:
            rx_client = self.cloudlink.getUserObject(message["id"])
            if rx_client == None:
                # Tell the client that the server failed to find a client with that ID
                await self.cloudlink.sendCode(client, "IDNotFound", listener_detected, listener_id)
                return

            if rx_client == LookupError:
                # Tell the client that the server needs the ID to be more specific
                await self.cloudlink.sendCode(client, "IDNotSpecific", listener_detected, listener_id)
                return

            if rx_client == TypeError:
                # Tell the client it sent an unsupported datatype
                await self.cloudlink.sendCode(client, "DataType", listener_detected, listener_id)
                return
            
            # Send the message to the recipient ID
            self.supporter.log(f"Client {client.id} ({client.full_ip}) sent private message data \"{message['val']}\" going to {rx_client.id} ({rx_client.full_ip})!")
            await self.cloudlink.sendPacket(rx_client, {"cmd": "pmsg", "val": message["val"], "origin": self.cloudlink.getUserObjectFromClientObj(client)}, rooms = room_id)

            # Tell the client that the message was successfully sent
            await self.cloudlink.sendCode(client, "OK", listener_detected, listener_id)
        
        # Fire callbacks
        if self.pmsg in self.cloudlink.usercallbacks:
            if self.cloudlink.usercallbacks[self.pmsg] != None:
                await self.cloudlink.usercallbacks[self.pmsg](value = message, origin = self.cloudlink.getUserObject(client))
    
    # Set username
    async def setid(self, client, message, listener_detected, listener_id, room_id):
        # Prevent clients from being able to rewrite their username
        if client.username_set:
            self.supporter.log(f"Client {client.id} ({client.full_ip}) specified username \"{message['val']}\", but username was already set to \"{client.friendly_username}\"")
            await self.cloudlink.sendCode(client, "IDSet", listener_detected, listener_id)
            return
        
        # Only support strings for usernames
        if not type(message["val"]) == str:
            self.supporter.log(f"Client {client.id} ({client.full_ip}) specified username \"{message['val']}\", but username is not the correct datatype!")
            await self.cloudlink.sendCode(client, "DataType", listener_detected, listener_id)
            return
        
        # Keep username sizes within a reasonable length
        if not len(message["val"]) in range(1, 21):
            self.supporter.log(f"Client {client.id} ({client.full_ip}) specified username \"{message['val']}\", but username is not within 1-20 characters!")
            await self.cloudlink.sendCode(client, "Refused", listener_detected, listener_id)
            return
        
        self.supporter.log(f"Client {client.id} ({client.full_ip}) specified username \"{message['val']}\"")
        client.friendly_username = str(message["val"])
        client.username_set = True
        # Report to the client that the username was accepted
        msg = {
            "username": client.friendly_username, 
            "id": client.id
        }
        await self.cloudlink.sendCode(client, "OK", listener_detected, listener_id, msg)

        # Update all clients with the updated userlist
        pages, size, ulist = self.supporter.paginate_ulist(self.cloudlink.getUsernames())
        await self.cloudlink.sendPacket(self.cloudlink.getAllUsersInRoom("default"), {"cmd": "ulist", "pages": pages, "size": size, "val": ulist})
        
        # Fire callbacks
        if self.setid in self.cloudlink.usercallbacks:
            if self.cloudlink.usercallbacks[self.setid] != None:
                await self.cloudlink.usercallbacks[self.setid](message)

    # WIP
    async def relay(self, client, message, listener_detected, listener_id, room_id):
        pass