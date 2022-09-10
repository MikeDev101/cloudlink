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
    def ulist(self, client, server, message, listener_detected, listener_id, room_id):
        for room in client.rooms:
            ulist = []
            for user in self.supporter.getUsernames(room):
                ulist.append(user)
            self.cloudlink.sendPacket(client, {"cmd": "ulist", "val": ulist}, rooms = room)

    # Status codes (For client-to-client)
    def statuscode(self, client, server, message, listener_detected, listener_id, room_id):
        # Sanity check the message
        for key in ["val", "id"]:
            if not key in message:
                self.cloudlink.sendCode(client, "Syntax", listener_detected, listener_id)
                return
        
        if type(message["id"]) == list:
            rx_client = self.supporter.selectMultiUserObjects(message["id"])
            if not(len(rx_client) == 0):
                # Send the message to all recipient IDs
                self.supporter.log(f"Client {client.id} ({client.full_ip}) is sending a status code to other clients!")
                self.cloudlink.sendPacket(rx_client, {"cmd": "statuscode", "code": message["val"], "origin": self.supporter.getUserObjectFromClientObj(client)})

                # Tell the client that all status codes were successfully sent
                self.cloudlink.sendCode(client, "OK", listener_detected, listener_id)
            else:
                # Tell the client that the server failed to find a client with those IDs
                self.cloudlink.sendCode(client, "IDNotFound", listener_detected, listener_id)
        else:
            rx_client = self.supporter.getUserObject(message["id"])
            if rx_client == None:
                # Tell the client that the server failed to find a client with that ID
                self.cloudlink.sendCode(client, "IDNotFound", listener_detected, listener_id)
                return

            if rx_client == LookupError:
                # Tell the client that the server needs the ID to be more specific
                self.cloudlink.sendCode(client, "IDNotSpecific", listener_detected, listener_id)
                return

            if rx_client == TypeError:
                # Tell the client it sent an unsupported datatype
                self.cloudlink.sendCode(client, "DataType", listener_detected, listener_id)
                return
            
            # Send the status code to the recipient ID
            self.supporter.log(f"Client {client.id} ({client.full_ip}) is sending a status code to {rx_client.id} ({rx_client.full_ip})!")
            self.cloudlink.sendPacket(rx_client, {"cmd": "statuscode", "code": message["val"], "origin": self.supporter.getUserObjectFromClientObj(client)}, rooms = room_id)

            # Tell the client that the status code was successfully sent
            self.cloudlink.sendCode(client, "OK", listener_detected, listener_id)

    # Ping
    def ping(self, client, server, message, listener_detected, listener_id, room_id):
        # Check if the client is pinging the server only
        if not "id" in message:
            self.supporter.log(f"Client {client.id} ({client.full_ip}) pinged the server!")
            self.cloudlink.sendCode(client, "OK", listener_detected, listener_id)
            return
        
        # Prevent clients without usernames from linking
        if not client.username_set:
            self.cloudlink.sendCode(client, "IDRequired", listener_detected, listener_id)
            return

        # Sanity check the message
        for key in ["val", "id"]:
            if not key in message:
                self.cloudlink.sendCode(client, "Syntax", listener_detected, listener_id)
                return

        if type(message["id"]) == list:
            rx_client = self.supporter.selectMultiUserObjects(message["id"])
            if not(len(rx_client) == 0):
                # Send the message to all recipient IDs
                self.supporter.log(f"Client {client.id} ({client.full_ip}) is pinging other clients!")
                self.cloudlink.sendPacket(rx_client, {"cmd": "ping", "val": message["val"], "origin": self.supporter.getUserObjectFromClientObj(client)})
                # Assume that each of the client's recipients will respond with a statuscode
            else:
                # Tell the client that the server failed to find a client with those IDs
                self.cloudlink.sendCode(client, "IDNotFound", listener_detected, listener_id)
        else:
            rx_client = self.supporter.getUserObject(message["id"])
            if rx_client == None:
                # Tell the client that the server failed to find a client with that ID
                self.cloudlink.sendCode(client, "IDNotFound", listener_detected, listener_id)
                return

            if rx_client == LookupError:
                # Tell the client that the server needs the ID to be more specific
                self.cloudlink.sendCode(client, "IDNotSpecific", listener_detected, listener_id)
                return

            if rx_client == TypeError:
                # Tell the client it sent an unsupported datatype
                self.cloudlink.sendCode(client, "DataType", listener_detected, listener_id)
                return
            
            self.supporter.log(f"Client {client.id} ({client.full_ip}) is sending a ping to {rx_client.id} ({rx_client.full_ip})!")
            # Send the ping to the recipient ID
            self.cloudlink.sendPacket(rx_client, {"cmd": "ping", "val": message["val"], "origin": self.supporter.getUserObjectFromClientObj(client)}, rooms = room_id)
            # Assume that the client's recipient will respond with a statuscode
    
    # Link client to a room/rooms
    def link(self, client, server, message, listener_detected, listener_id, room_id):
        self.supporter.log(f"Client {client.id} ({client.full_ip}) is linking to room(s): {message['val']}")

        # Temporarily save the client's old rooms data
        old_rooms = client.rooms

        # Prevent clients without usernames from linking
        if not client.username_set:
            self.cloudlink.sendCode(client, "IDRequired", listener_detected, listener_id)
            return
        
        # Sanity check the message
        if not "val" in message:
            self.cloudlink.sendCode(client, "Syntax", listener_detected, listener_id)
            return

        if type(message["val"]) in [list, str]:
            # Convert to set
            if type(message["val"]) == str:
                message["val"] = set([message["val"]])
            elif type(message["val"]) == list:
                message["val"] = set(message["val"])

            # Remove the client from all rooms and set their room to the default room
            self.supporter.unlinkClientFromRooms(client)

            # Add client to rooms
            self.supporter.linkClientToRooms(client, message["val"])

            # Tell the client that they were linked
            self.cloudlink.sendCode(client, "OK", listener_detected, listener_id)

            # Update all client ulists for the default room
            if "default" in old_rooms:
                self.cloudlink.sendPacket(self.supporter.getAllUsersInRoom("default"), {"cmd": "ulist", "val": self.supporter.getUsernames()})

            # Update all client ulists in the rooms that the client joined
            self.cloudlink.sendPacket(self.supporter.getAllUsersInManyRooms(message["val"]), {"cmd": "ulist", "val": self.supporter.getUsernames(message["val"])}, rooms = message["val"])

        else:
            self.cloudlink.sendCode(client, "Datatype", listener_detected, listener_id)
    
    # Unlink client from all rooms, and then link the client to the default room
    def unlink(self, client, server, message, listener_detected, listener_id, room_id):
        self.supporter.log(f"Client {client.id} ({client.full_ip}) unlinking from all rooms")

        # Prevent clients without usernames from using this command
        if not client.username_set:
            self.cloudlink.sendCode(client, "IDRequired", listener_detected, listener_id)
            return
        
        if client.is_linked:
            # Temporarily save the client's old rooms data
            old_rooms = client.rooms

            # Remove the client from all rooms and set their room to the default room
            self.supporter.unlinkClientFromRooms(client)

            # Tell the client that they were unlinked
            self.cloudlink.sendCode(client, "OK", listener_detected, listener_id)

            # Update all client ulists for the default room
            self.cloudlink.sendPacket(self.supporter.getAllUsersInRoom("default"), {"cmd": "ulist", "val": self.supporter.getUsernames()})

            # Update all client ulists in the room that the client left
            self.cloudlink.sendPacket(self.supporter.getAllUsersInManyRooms(old_rooms), {"cmd": "ulist", "val": self.supporter.getUsernames(old_rooms)}, rooms = old_rooms)
        else:
            self.supporter.log(f"Client {client.id} ({client.full_ip}) was already unlinked!")
            # Tell the client that it was already unlinked
            self.cloudlink.sendCode(client, "OK", listener_detected, listener_id)

            # Give the client the default room ulist
            self.cloudlink.sendPacket(client, {"cmd": "ulist", "val": self.supporter.getUsernames()})
    
    # Direct messages, this command is pretty obsolete, since custom commands are loaded directly into Cloudlink instead of using direct in CL3. Idfk what this should do.
    def direct(self, client, server, message, listener_detected, listener_id, room_id):
        # Sanity check the message
        if not "id" in message:
            self.cloudlink.sendCode(client, "Syntax", listener_detected, listener_id)
            return

        self.supporter.log(f"Client {client.id} ({client.full_ip}) sent direct data: \"{message}\"")

        if type(message["id"]) == list:
            rx_client = self.supporter.selectMultiUserObjects(message["id"])
            if not(len(rx_client) == 0):
                # Send the message to all recipient IDs
                self.supporter.log(f"Client {client.id} ({client.full_ip}) is sending direct data to various clients!")
                self.cloudlink.sendPacket(rx_client, {"cmd": "direct", "val": message["val"], "origin": self.supporter.getUserObjectFromClientObj(client)})

                # Tell the client that all direct data were successfully sent
                self.cloudlink.sendCode(client, "OK", listener_detected, listener_id)
            else:
                # Tell the client that the server failed to find a client with those IDs
                self.cloudlink.sendCode(client, "IDNotFound", listener_detected, listener_id)
        else:
            rx_client = self.supporter.getUserObject(message["id"])
            if rx_client == None:
                # Tell the client that the server failed to find a client with that ID
                self.cloudlink.sendCode(client, "IDNotFound", listener_detected, listener_id)
                return

            if rx_client == LookupError:
                # Tell the client that the server needs the ID to be more specific
                self.cloudlink.sendCode(client, "IDNotSpecific", listener_detected, listener_id)
                return

            if rx_client == TypeError:
                # Tell the client it sent an unsupported datatype
                self.cloudlink.sendCode(client, "DataType", listener_detected, listener_id)
                return

            self.supporter.log(f"Client {client.id} ({client.full_ip}) is sending direct data to {rx_client.id} ({rx_client.full_ip})!")
            # Send the ping to the recipient ID
            self.cloudlink.sendPacket(rx_client, {"cmd": "direct", "val": message["val"], "name": message["name"], "origin": self.supporter.getUserObjectFromClientObj(client)}, rooms = room_id)

            # Tell the client that the direct data was successfully sent
            self.cloudlink.sendCode(client, "OK", listener_detected, listener_id)
    
    # Global messages
    def gmsg(self, client, server, message, listener_detected, listener_id, room_id):
        self.supporter.log(f"Client {client.id} ({client.full_ip}) sent global message with data \"{message['val']}\"")

        # Send the message to all clients except the origin
        ulist = self.supporter.getAllUsersInManyRooms(room_id)
        ulist.remove(client)
        msg = {
            "cmd": "gmsg",
            "val": message["val"]
        }
        self.cloudlink.sendPacket(ulist, msg, rooms=room_id)

        # Send the message back to origin
        self.cloudlink.sendPacket(client, msg, listener_detected, listener_id, room_id)

        # Cache the last message for new clients
        self.cloudlink.global_msg = message["val"]

    # Global cloud variables
    def gvar(self, client, server, message, listener_detected, listener_id, room_id):

        # Sanity check the message
        for key in ["val", "name"]:
            if not key in message:
                self.cloudlink.sendCode(client, "Syntax", listener_detected, listener_id)
                return

        self.supporter.log(f"Client {client.id} ({client.full_ip}) sent global variable with data \"{message['val']}\"")

        # Send the message to all clients except the origin
        ulist = self.supporter.getAllUsersInManyRooms(room_id)
        ulist.remove(client)
        msg = {
            "cmd": "gvar",
            "val": message["val"],
            "name": message["name"]
        }
        self.cloudlink.sendPacket(ulist, msg, rooms=room_id)

        # Send the message back to origin
        self.cloudlink.sendPacket(client, msg, listener_detected, listener_id, room_id)
    
    # Private cloud variables
    def pvar(self, client, server, message, listener_detected, listener_id, room_id):
        # Prevent clients without usernames from using this command
        if not client.username_set:
            self.cloudlink.sendCode(client, "IDRequired", listener_detected, listener_id)
            return
        
        # Sanity check the message
        for key in ["val", "name", "id"]:
            if not key in message:
                self.cloudlink.sendCode(client, "Syntax", listener_detected, listener_id)
                return
        
        if type(message["id"]) == list:
            rx_client = self.supporter.selectMultiUserObjects(message["id"])
            if not(len(rx_client) == 0):
                # Send the message to all recipient IDs
                self.supporter.log(f"Client {client.id} ({client.full_ip}) sent private variable data \"{message['val']}\" going to various clients!")
                self.cloudlink.sendPacket(rx_client, {"cmd": "pvar", "val": message["val"], "name": message["name"], "origin": self.supporter.getUserObjectFromClientObj(client)}, rooms = room_id)

                # Tell the client that the messages were successfully sent
                self.cloudlink.sendCode(client, "OK", listener_detected, listener_id)
            else:
                # Tell the client that the server failed to find a client with those IDs
                self.cloudlink.sendCode(client, "IDNotFound", listener_detected, listener_id)
        else:
            rx_client = self.supporter.getUserObject(message["id"])
            if rx_client == None:
                # Tell the client that the server failed to find a client with that ID
                self.cloudlink.sendCode(client, "IDNotFound", listener_detected, listener_id)
                return

            if rx_client == LookupError:
                # Tell the client that the server needs the ID to be more specific
                self.cloudlink.sendCode(client, "IDNotSpecific", listener_detected, listener_id)
                return

            if rx_client == TypeError:
                # Tell the client it sent an unsupported datatype
                self.cloudlink.sendCode(client, "DataType", listener_detected, listener_id)
                return

            # Send the message to the recipient ID
            self.supporter.log(f"Client {client.id} ({client.full_ip}) sent private variable data \"{message['val']}\" going to {rx_client.id} ({rx_client.full_ip})!")
            self.cloudlink.sendPacket(rx_client, {"cmd": "pvar", "val": message["val"], "name": message["name"], "origin": self.supporter.getUserObjectFromClientObj(client)}, rooms = room_id)

            # Tell the client that the message was successfully sent
            self.cloudlink.sendCode(client, "OK", listener_detected, listener_id)
    
    # Private messages
    def pmsg(self, client, server, message, listener_detected, listener_id, room_id):
        # Prevent clients without usernames from using this command
        if not client.username_set:
            self.cloudlink.sendCode(client, "IDRequired", listener_detected, listener_id)
            return

        # Sanity check the message
        for key in ["val", "id"]:
            if not key in message:
                self.cloudlink.sendCode(client, "Syntax", listener_detected, listener_id)
                return
        
        if type(message["id"]) == list:
            rx_client = self.supporter.selectMultiUserObjects(message["id"])
            if not(len(rx_client) == 0):
                # Send the message to all recipient IDs
                self.supporter.log(f"Client {client.id} ({client.full_ip}) sent private messsage data \"{message['val']}\" going to various clients!")
                self.cloudlink.sendPacket(rx_client, {"cmd": "pmsg", "val": message["val"], "origin": self.supporter.getUserObjectFromClientObj(client)})

                # Tell the client that the messages were successfully sent
                self.cloudlink.sendCode(client, "OK", listener_detected, listener_id)
            else:
                # Tell the client that the server failed to find a client with those IDs
                self.cloudlink.sendCode(client, "IDNotFound", listener_detected, listener_id)
        else:
            rx_client = self.supporter.getUserObject(message["id"])
            if rx_client == None:
                # Tell the client that the server failed to find a client with that ID
                self.cloudlink.sendCode(client, "IDNotFound", listener_detected, listener_id)
                return

            if rx_client == LookupError:
                # Tell the client that the server needs the ID to be more specific
                self.cloudlink.sendCode(client, "IDNotSpecific", listener_detected, listener_id)
                return

            if rx_client == TypeError:
                # Tell the client it sent an unsupported datatype
                self.cloudlink.sendCode(client, "DataType", listener_detected, listener_id)
                return
            
            # Send the message to the recipient ID
            self.supporter.log(f"Client {client.id} ({client.full_ip}) sent private message data \"{message['val']}\" going to {rx_client.id} ({rx_client.full_ip})!")
            self.cloudlink.sendPacket(rx_client, {"cmd": "pmsg", "val": message["val"], "origin": self.supporter.getUserObjectFromClientObj(client)}, rooms = room_id)

            # Tell the client that the message was successfully sent
            self.cloudlink.sendCode(client, "OK", listener_detected, listener_id)
    
    # Set username
    def setid(self, client, server, message, listener_detected, listener_id, room_id):
        # Prevent clients from being able to rewrite their username
        if client.username_set:
            self.supporter.log(f"Client {client.id} ({client.full_ip}) specified username \"{message['val']}\", but username was already set to \"{client.friendly_username}\"")
            self.cloudlink.sendCode(client, "IDSet", listener_detected, listener_id)
            return
        
        # Only support strings for usernames
        if not type(message["val"]) == str:
            self.supporter.log(f"Client {client.id} ({client.full_ip}) specified username \"{message['val']}\", but username is not the correct datatype!")
            self.cloudlink.sendCode(client, "DataType", listener_detected, listener_id)
            return
        
        # Keep username sizes within a reasonable length
        if not len(message["val"]) in range(1, 21):
            self.supporter.log(f"Client {client.id} ({client.full_ip}) specified username \"{message['val']}\", but username is not within 1-20 characters!")
            self.cloudlink.sendCode(client, "Refused", listener_detected, listener_id)
            return
        
        self.supporter.log(f"Client {client.id} ({client.full_ip}) specified username \"{message['val']}\"")
        client.friendly_username = str(message["val"])
        client.username_set = True
        # Report to the client that the username was accepted
        msg = {
            "username": client.friendly_username, 
            "id": client.id
        }
        self.cloudlink.sendCode(client, "OK", listener_detected, listener_id, msg)

        # Update all clients with the updated userlist
        self.cloudlink.sendPacket(self.supporter.getAllUsersInRoom("default"), {"cmd": "ulist", "val": self.supporter.getUsernames()})

    # WIP
    def relay(self, client, server, message, listener_detected, listener_id, room_id):
        pass