class serverInternalHandlers():
    """
    The serverInternalHandlers inter class serves as the server's built-in command handler.
    These commands are hard-coded per-spec as outlined in the CLPv4 (Cloudlink Protocol) guideline.
    """
    
    def __init__(self, cloudlink):
        self.cloudlink = cloudlink
        self.supporter = self.cloudlink.supporter
    
    # Link client to a room/rooms
    def link(self, client, server, message, listener_detected, listener_id, room_id):
        self.supporter.log(f"Client {client['id']} ({client['address']}) is linking to room(s): {message['val']}")
        if self.supporter.readAttrFromClient(client)["username_set"]:
            if type(message["val"]) in [list, str]:
                # Convert to list
                if type(message["val"]) == str:
                    message["val"] = [message["val"]]

                # Add client to rooms
                if not self.supporter.readAttrFromClient(client)["is_linked"]:
                    self.supporter.writeAttrToClient(client, "is_linked", True)
                self.supporter.writeAttrToClient(client, "rooms", message["val"])
                self.cloudlink.sendCode(client, "OK", listener_detected, listener_id)

                # Update all client ulists for the default room
                self.cloudlink.sendPacket(self.cloudlink.all_clients, {"cmd": "ulist", "val": self.supporter.getUsernames()}, listener_detected, listener_id)

                # Update all client ulists in the room that the client joined
                self.cloudlink.sendPacket(self.cloudlink.all_clients, {"cmd": "ulist", "val": self.supporter.getUsernames(message["val"])}, listener_detected, listener_id, message["val"])

            else:
                self.cloudlink.sendCode(client, "Datatype", listener_detected, listener_id)
        else:
            self.cloudlink.sendCode(client, "IDRequired", listener_detected, listener_id)
    
    # Unlink client from all rooms, and then link the client to the default room
    def unlink(self, client, server, message, listener_detected, listener_id, room_id):
        self.supporter.log(f"Client {client['id']} ({client['address']}) unlinking from all rooms")
        if self.supporter.readAttrFromClient(client)["username_set"]:
            # Temporarily save the client's old rooms data
            old_rooms = self.supporter.readAttrFromClient(client)["rooms"]

            # Remove the client from all rooms and set their room to the default room
            if self.supporter.readAttrFromClient(client)["is_linked"]:
                self.supporter.writeAttrToClient(client, "is_linked", False)
            self.supporter.writeAttrToClient(client, "rooms", ["default"])
            self.cloudlink.sendCode(client, "OK", listener_detected, listener_id, room_id)

            # Update all client ulists for the default room
            self.cloudlink.sendPacket(self.cloudlink.all_clients, {"cmd": "ulist", "val": self.supporter.getUsernames()}, listener_detected, listener_id)

            # Update all client ulists in the room that the client left
            self.cloudlink.sendPacket(self.cloudlink.all_clients, {"cmd": "ulist", "val": self.supporter.getUsernames(old_rooms)}, listener_detected, listener_id, old_rooms)
        else:
            self.cloudlink.sendCode(client, "IDRequired", listener_detected, listener_id)
    
    # Direct messages
    def direct(self, client, server, message, listener_detected, listener_id, room_id):
        self.supporter.log(f"Client {client['id']} ({client['address']}) sent direct data: \"{message}\"")
        # This functionality is pretty obsolete, since custom commands are loaded directly into Cloudlink instead of using direct in CL3. Idfk what this should do.
    
    # Global messages
    def gmsg(self, client, server, message, listener_detected, listener_id, room_id):

        self.supporter.log(f"Client {client['id']} ({client['address']}) sent global message with data \"{message['val']}\"")

        # Send the message to all clients except the origin
        ulist = self.cloudlink.all_clients.copy()
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
        self.supporter.log(f"Client {client['id']} ({client['address']}) sent global variable with data \"{message['val']}\"")

        # Send the message to all clients except the origin
        ulist = self.cloudlink.all_clients.copy()
        ulist.remove(client)
        msg = {
            "cmd": "gvar",
            "val": message["val"],
            "name": message["name"]
        }
        self.cloudlink.sendPacket(ulist, msg, rooms=room_id)

        # Send the message back to origin
        self.cloudlink.sendPacket(client, msg, listener_detected, listener_id)
    
    # Private cloud variables
    def pvar(self, client, server, message, listener_detected, listener_id, room_id):
        self.supporter.log(f"Client {client['id']} ({client['address']}) sent private message with data \"{message['val']}\" going to {message['id']}")
        if self.supporter.readAttrFromClient(client)["username_set"]:
            if type(message["id"]) == list:
                rx_client = self.supporter.selectMultiUserObjects(message["id"])
                if not(len(rx_client) == 0):
                    # Send the message to all recipient IDs
                    self.cloudlink.sendPacket(rx_client, {"cmd": "pvar", "val": message["val"], "name": message["name"], "origin": self.supporter.getUserObjectFromClientObj(client)}, room_id = room_id)

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

                elif rx_client == LookupError:
                    # Tell the client that the server needs the ID to be more specific
                    self.cloudlink.sendCode(client, "IDNotSpecific", listener_detected, listener_id)

                elif rx_client == TypeError:
                    # Tell the client it sent an unsupported datatype
                    self.cloudlink.sendCode(client, "DataType", listener_detected, listener_id)

                else:
                    # Send the message to the recipient ID
                    self.cloudlink.sendPacket(rx_client, {"cmd": "pvar", "val": message["val"], "name": message["name"], "origin": self.supporter.getUserObjectFromClientObj(client)}, rooms = room_id)

                    # Tell the client that the message was successfully sent
                    self.cloudlink.sendCode(client, "OK", listener_detected, listener_id)
        else:
            # Tell the client that it needs to set a username first
            self.cloudlink.sendPacket(client, {"cmd": "statuscode", "code": self.supporter.codes["IDRequired"]}, listener_detected, listener_id, room_id)
    
    # Private messages
    def pmsg(self, client, server, message, listener_detected, listener_id, room_id):
        self.supporter.log(f"Client {client['id']} ({client['address']}) sent private message with data \"{message['val']}\" going to {message['id']}")
        if self.supporter.readAttrFromClient(client)["username_set"]:
            if type(message["id"]) == list:
                rx_client = self.supporter.selectMultiUserObjects(message["id"])
                if not(len(rx_client) == 0):
                    # Send the message to all recipient IDs
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

                elif rx_client == LookupError:
                    # Tell the client that the server needs the ID to be more specific
                    self.cloudlink.sendCode(client, "IDNotSpecific", listener_detected, listener_id)

                elif rx_client == TypeError:
                    # Tell the client it sent an unsupported datatype
                    self.cloudlink.sendCode(client, "DataType", listener_detected, listener_id)

                else:
                    # Send the message to the recipient ID
                    self.cloudlink.sendPacket(rx_client, {"cmd": "pmsg", "val": message["val"], "origin": self.supporter.getUserObjectFromClientObj(client)}, rooms = room_id)

                    # Tell the client that the message was successfully sent
                    self.cloudlink.sendCode(client, "OK", listener_detected, listener_id)
        else:
            # Tell the client that it needs to set a username first
            self.cloudlink.sendPacket(client, {"cmd": "statuscode", "code": self.supporter.codes["IDRequired"]}, listener_detected, listener_id, room_id)
    
    # Set username
    def setid(self, client, server, message, listener_detected, listener_id, room_id):
        # Prevent clients from being able to rewrite their username
        if not self.supporter.readAttrFromClient(client)["username_set"]:
            # Only support strings for usernames
            if type(message["val"]) == str:
                # Keep username sizes within a reasonable length
                if len(message["val"]) in range(1, 21):
                    self.supporter.log(f"Client {client['id']} ({client['address']}) specified username \"{message['val']}\"")
                    self.supporter.writeAttrToClient(client, "friendly_username", str(message["val"]))
                    self.supporter.writeAttrToClient(client, "username_set", True)

                    # Report to the client that the username was accepted
                    clientAttrs = self.supporter.readAttrFromClient(client)
                    msg = {
                        "username": clientAttrs["friendly_username"], 
                        "id": client['id']
                    }
                    self.cloudlink.sendCode(client, "OK", listener_detected, listener_id, msg)

                    # Update all clients with the updated userlist
                    self.cloudlink.sendPacket(self.cloudlink.all_clients, {"cmd": "ulist", "val": self.supporter.getUsernames()})

                else:
                    self.supporter.log(f"Client {client['id']} ({client['address']}) specified username \"{message['val']}\", but username is not within 1-20 characters!")
                    self.cloudlink.sendCode(client, "Refused", listener_detected, listener_id)
            else:
                self.supporter.log(f"Client {client['id']} ({client['address']}) specified username \"{message['val']}\", but username is not the correct datatype!")
                self.cloudlink.sendCode(client, "Datatype", listener_detected, listener_id)
        else:
            existing_username = self.supporter.readAttrFromClient(client)["friendly_username"]
            self.supporter.log(f"Client {client['id']} ({client['address']}) specified username \"{message['val']}\", but username was already set to \"{existing_username}\"")
            self.cloudlink.sendCode(client, "IDSet", listener_detected, listener_id)