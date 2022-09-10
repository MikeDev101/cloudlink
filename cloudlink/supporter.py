from datetime import datetime
import traceback
import sys
import json

class supporter:
    """
    This module provides extended functionality for Cloudlink. This class is shared between the server and client modes.
    """

    def __init__(self, cloudlink, enable_logs, mode:int):
        self.cloudlink = cloudlink
        self.json = json
        self.datetime = datetime
        self.enable_logs = enable_logs
        self.codes = {
            "Test": "I:100 | Test",
            "OK": "I:100 | OK",
            "Syntax": "E:101 | Syntax",
            "DataType": "E:102 | Datatype",
            "IDNotFound": "E:103 | ID not found",
            "IDNotSpecific": "E:104 | ID not specific enough",
            "InternalServerError": "E:105 | Internal server error",
            "EmptyPacket": "E:106 | Empty packet",
            "IDSet": "E:107 | ID already set",
            "Refused": "E:108 | Refused",
            "Invalid": "E:109 | Invalid command",
            "Disabled": "E:110 | Command disabled",
            "IDRequired": "E:111 | ID required",
        }
        
        if mode == None:
            raise TypeError("Mode cannot be None, or any value other than 1 or 0!")
        else:
            if mode == 1:
                setattr(self, "sendPacket", self._sendPacket_server)
            elif mode == 2:
                setattr(self, "sendPacket", self._sendPacket_client)
            else:
                raise NotImplementedError("Invalid supporter mode")
    
    def sendCode(self, client:dict, code:str, listener_detected:bool = False, listener_id:str = "", extra_data = None):
        message = {
            "cmd": "statuscode",
            "code": self.codes[code]
        }

        if extra_data != None:
            message["val"] = extra_data

        if listener_detected:
            message["listener"] = listener_id

        self.cloudlink.wss.send_message(client, self.json.dumps(message))
    
    def _sendPacket_client(self, message):
        try:
            self.log(f"Sending packet: {message}")
            self.cloudlink.wss.send(self.json.dumps(message))
        except BrokenPipeError:
            self.log(f"Broken Pipe Error: Attempted to send packet {message}!")
        except Exception as e:
            self.log(f"Exception: {e}, Attempted to send packet {message}!")
    
    def _sendPacket_server(self, clients, message:dict, listener_detected:bool = False, listener_id:str = "", rooms:list = None, ignore_rooms:bool = False):
        if type(message) == dict:
            if self.isPacketSane(message, ["cmd"]):
                # Attach listener (if applied to origin message)
                if listener_detected:
                    message["listener"] = listener_id

                # Convert clients to set
                if type(clients) == list:
                    clients = set(clients)
                if type(clients) != set:
                    clients = set([clients])
                
                # Convert rooms to set
                if type(rooms) == list:
                    rooms = set(rooms)
                if type(rooms) != set:
                    rooms = set([rooms])
                
                # Send to all specified clients
                for client in clients:
                    if not ignore_rooms:
                        for room in rooms:
                            if room in ["default", None]:
                                room = "default"
                            else:
                                message["room"] = room
                            if room in list(client.rooms):
                                self.log(f"Sending packet to client {client.id} ({client.full_ip}): {message}")
                                try:
                                    self.cloudlink.wss.send_message(client, self.json.dumps(message))
                                except BrokenPipeError:
                                    self.log(f"Broken Pipe Error: Attempted to send packet {message} to {client.id} ({client.full_ip})!")
                                except Exception as e:
                                    self.log(f"Exception: {e}, Attempted to send packet {message} to {client.id} ({client.full_ip})!")
                    else:
                        self.log(f"Sending packet to client (while ignoring rooms) {client.id} ({client.full_ip}): {message}")
                        try:
                            self.cloudlink.wss.send_message(client, self.json.dumps(message))
                        except BrokenPipeError:
                            self.log(f"Broken Pipe Error: Attempted to send packet {message} to {client.id} ({client.full_ip}) (while ignoring rooms)!")
                        except Exception as e:
                            self.log(f"Exception: {e}, Attempted to send packet {message} to {client.id} ({client.full_ip}) (while ignoring rooms)!")
                            
    
    def setClientUsername(self, client, username):
        if type(username) == str:
            if client in self.cloudlink.all_clients:
                if not client.username_set:
                    self.log(f"Setting client {client.id} ({client.full_ip}) username to \"{username}\"...")
                    client.friendly_username = username
                    client.username_set = True
        else:
            raise TypeError
    
    def linkClientToRooms(self, client, rooms):
        if type(rooms) in [str, list, set]:
            if client in self.cloudlink.all_clients:
                # Convert to set
                if type(rooms) in [list, str]:
                    if type(rooms) == str:
                        rooms = set([rooms])
                    elif type(rooms) == list:
                        rooms = set(rooms)
                self.log(f"Linking client {client.id} ({client.full_ip}) to rooms {list(rooms)}...")

                # Remove client from all rooms
                self.removeClientFromAllRooms(client)

                # Add client to new rooms
                self.roomHandler(1, client, rooms)
                client.rooms = rooms

                # Marked as linked
                client.is_linked = True
        else:
            raise TypeError
    
    def unlinkClientFromRooms(self, client):
        if client in self.cloudlink.all_clients: 
            self.log(f"Unlinking client {client.id} ({client.full_ip}) from rooms...")
            # Remove client from all rooms
            self.removeClientFromAllRooms(client)

            # Add client to default room
            client.rooms = ["default"]
            self.roomHandler(1, client, ["default"])

            # Mark as not linked
            client.is_linked = False
    
    def removeClientFromAllRooms(self, client):
        if client in self.cloudlink.all_clients: 
            self.roomHandler(2, client, client.rooms)

    def roomHandler(self, mode, client, room_ids):
        if type(room_ids) == str:
            room_ids = set([room_ids])
        elif type(room_ids) == list:
            room_ids = set(room_ids)
        elif type(room_ids) == set:
            pass
        else:
            raise TypeError
        if mode == 1: # Create rooms
            for room in room_ids:
                self.joinRoom(room, client)
        elif mode == 2: # Leave rooms
            for room in room_ids:
                self.leaveRoom(room, client)
        else:
            raise NotImplementedError

    def joinRoom(self, room_id, client):
        # Automatically create rooms
        if not room_id in self.cloudlink.roomData:
            self.cloudlink.roomData[room_id] = set()
        
        # Add the client object to the room
        if not client in self.cloudlink.roomData[room_id]:
            self.cloudlink.roomData[room_id].add(client)

    def leaveRoom(self, room_id, client):
        # Check if room exists
        if room_id in self.cloudlink.roomData:
            # Check if client object is in the room
            if client in self.cloudlink.roomData[room_id]:
                self.cloudlink.roomData[room_id].discard(client)
            
            # Automatically remove empty rooms, and prevent accidental deletion of the default room
            if (len(self.cloudlink.roomData[room_id]) == 0) and (room_id != "default"): 
                del self.cloudlink.roomData[room_id]

    def getAllUsersInManyRooms(self, room_ids = ["default"]):
        # Bugfix
        if room_ids == None:
            room_ids = set(["default"])
        
        # Convert to set
        if type(room_ids) == str:
            room_ids = set([room_ids])
        elif type(room_ids) == list:
            room_ids = set(room_ids)
        elif type(room_ids) == set:
            pass
        else:
            raise TypeError
        allclients = []
        for room in room_ids:
            tmp = self.getAllUsersInRoom(room)
            for tmp_add in tmp:
                if not tmp_add in allclients:
                    allclients.append(tmp_add)
        return allclients
    
    def getAllUsersInRoom(self, room_id):
        if type(room_id) != str:
            raise TypeError
        if room_id in self.cloudlink.roomData:
            return self.cloudlink.roomData[room_id]
        else:
            return []
    
    def getAllRooms(self):
        return list(self.cloudlink.roomData.keys())
    
    def getAllClientRooms(self, client):
        roomlist = set()
        for room in client.rooms:
            roomlist.add(room)
        return roomlist

    def rejectClient(self, client, reason):
        if client in self.cloudlink.all_clients:
            client.send_close(1000, bytes(reason, encoding='utf-8'))
            self.cloudlink.wss._terminate_client_handler(client)

    def callback(self, callback_id, function):
        # Support older servers which use the old callback system.
        if type(callback_id) == str:
            callback_id = getattr(self.cloudlink, callback_id)
        
        # New callback system.
        if callable(callback_id):
            if hasattr(self.cloudlink, callback_id.__name__):
                self.log(f"Creating callback for {callback_id.__name__} to function {function.__name__}...")
                self.cloudlink.usercallbacks[callback_id] = function

    def full_stack(self):
        exc = sys.exc_info()[0]
        if exc is not None:
            f = sys.exc_info()[-1].tb_frame.f_back
            stack = traceback.extract_stack(f)
        else:
            stack = traceback.extract_stack()[:-1]
        trc = 'Traceback (most recent call last):\n'
        stackstr = trc + ''.join(traceback.format_list(stack))
        if exc is not None:
            stackstr += '  ' + traceback.format_exc().lstrip(trc)
        return stackstr

    def disableCommands(self, functions):
        for functionEntry in functions:
            if not functionEntry in self.cloudlink.disabledCommands:
                self.cloudlink.disabledCommands.append(functionEntry)
            if (not("__" in functionEntry) and (hasattr(self.cloudlink, functionEntry))): 
                if functionEntry in self.cloudlink.builtInCommands:
                    self.cloudlink.builtInCommands.remove(functionEntry)
                    delattr(self.cloudlink, str(functionEntry))
                elif functionEntry in self.cloudlink.customCommands:
                    self.cloudlink.customCommands.remove(functionEntry)
                    delattr(self.cloudlink, str(functionEntry))
                else:
                    self.log(f"Attempted to disable command {functionEntry} but either the command was already unloaded, it was not valid, or was not loaded beforehand.");

    def loadCustomCommands(self, classes, custom:dict = None):
        # Make it not require putting single classes into a list.
        if type(classes) == type:
            classes = [classes]

        # Load the classes
        if type(classes) == list:
            for classEntry in classes:
                if type(classEntry) == type:
                    # Get an array of attributes from class
                    classFunctions = dir(classEntry)
                    
                    # Create a new inter class within self and initialize it
                    if not hasattr(self.cloudlink, str(classEntry)):

                        if (custom != None) and (classEntry in custom):
                            setattr(self.cloudlink, str(classEntry), classEntry(self.cloudlink, custom[classEntry]))
                        else:
                            setattr(self.cloudlink, str(classEntry), classEntry(self.cloudlink))
                    
                    for functionEntry in classFunctions:
                        # Check if a function within class is a private function
                        try:
                            if ((not("__" in functionEntry)) and (not(hasattr(self.cloudlink, functionEntry)))):
                                # Check if a function is marked as ignore
                                shouldAdd = True
                                if hasattr(getattr(self.cloudlink, str(classEntry)), "importer_ignore_functions"):
                                    if type(getattr(self.cloudlink, str(classEntry)).importer_ignore_functions) == list:
                                        if str(functionEntry) in getattr(self.cloudlink, str(classEntry)).importer_ignore_functions:
                                            shouldAdd = False
                            
                                if shouldAdd:
                                    setattr(self.cloudlink, str(functionEntry), getattr(getattr(self.cloudlink, str(classEntry)), str(functionEntry)))
                                    self.cloudlink.customCommands.append(str(functionEntry))
                        except:
                            self.log(f"An exception has occurred whilst loading a custom command: {self.full_stack()}")
                else:
                    raise TypeError(f"Attempted to load \"{str(classEntry)}\", which is not a class!")
    
    def loadBuiltinCommands(self, handlerObject):
        # Get an array of attributes from self.serverInternalHandlers
        classFunctions = dir(handlerObject)
        for functionEntry in classFunctions:
            # Check if a function within self.serverInternalHandlers is a private function
            if (not("__" in functionEntry) and (not(hasattr(self.cloudlink, functionEntry)))): 
                try:
                    # Check if a function is marked as ignore
                    shouldAdd = True
                    if hasattr(handlerObject, "importer_ignore_functions"):
                        if type(handlerObject.importer_ignore_functions) == list:
                            if str(functionEntry) in handlerObject.importer_ignore_functions:
                                shouldAdd = False
                
                    if shouldAdd:
                        self.cloudlink.builtInCommands.append(str(functionEntry))
                        setattr(self.cloudlink, str(functionEntry), getattr(handlerObject, str(functionEntry)))
                except:
                    self.log(f"An exception has occurred whilst loading a built-in command: {self.full_stack()}")

    def getUsernames(self, rooms:list = ["default"]):
        userlist = []
        if type(rooms) in [str, list, set]:
            if type(rooms) == str:
                rooms = set([rooms])
            elif type(rooms) == list:
                rooms = set(rooms)
        else:
            raise TypeError
        for room in rooms:
            for client in self.getAllUsersInRoom(room):
                result = self.getUserObjectFromClientObj(client)
                if result != None:
                    if not result in userlist:
                        userlist.append(result)
        return userlist

    def getUserObjectFromClientObj(self, client):
        if client in self.cloudlink.all_clients:
            if client.username_set:
                return {
                    "username": client.friendly_username, 
                    "id": client.id
                }

    def selectMultiUserObjects(self, identifiers:list, rooms:list = ["default"]):
        # Implement multicast support
        objList = []
        if type(identifiers) == list:
            for client in identifiers:
                obj = self.getUserObject(client)
                # TODO: optimize this fugly mess
                if not obj in [TypeError, LookupError, None]:
                    for room in rooms:
                        if room in obj.rooms:
                            if not obj in objList:
                                objList.append(obj)
            return objList
        else:
            return TypeError

    def getUserObject(self, identifier):
        # NOT RECOMMENDED - Try to find the client object with a username
        if type(identifier) == str:
            clientIDs = []
            clientObjs = []
            for client in self.cloudlink.all_clients:
                clientIDs.append(client.friendly_username)
                clientObjs.append(client)
            
            if identifier in clientIDs:
                # Sort
                selectionTmp = []
                for read in clientIDs:
                    if read == identifier:
                        selectionTmp.append(read)
                # Return result
                if len(selectionTmp) > 1:
                    return LookupError # There are more than one clients with that username
                elif len(selectionTmp) == 0:
                    return None # No client found
                else:
                    return clientObjs[clientIDs.index(identifier)]

        # BEST PRACTICE - Identify client object using it's websocket object number
        elif type(identifier) == int:
            clientIDs = []
            clientObjs = []
            for client in self.cloudlink.all_clients:
                clientIDs.append(client.id)
                clientObjs.append(client)
            
            if identifier in clientIDs:
                return clientObjs[clientIDs.index(identifier)]
    
        # UGLY BUT WORKS - Identify client object using the output of supporter.getUserlist / serverInternalHandlers.setid ({"username": "", "id": ""} pairing for clients)
        elif type(identifier) == dict:
            clientIDs = []
            clientObjs = []
            for client in self.cloudlink.all_clients:
                clientIDs.append(client.id)
                clientObjs.append(client)
            
            if identifier["id"] in clientIDs:
                return clientObjs[clientIDs.index(identifier["id"])]
        
        # Unsupported type
        else:
            return TypeError

    def getClientObjFromUsername(self, username):
        return self.getUserObject(username)

    def createAttrForClient(self, client):
        client.friendly_username = ""
        client.username_set = False
        client.rooms = ["default"]
        client.is_linked = False

    def log(self, event):
        if self.enable_logs:
            print(f"{self.timestamp()}: {event}")

    def timestamp(self):
        today = self.datetime.now()
        return today.strftime("%m/%d/%Y %H:%M.%S")

    def isJSON(self, jsonStr):
        is_valid_json = False
        try:
            if type(jsonStr) == dict:
                is_valid_json = True
            elif type(jsonStr) == str:
                jsonStr = self.json.loads(jsonStr)
                is_valid_json = True
        except:
            is_valid_json = False
        return is_valid_json

    def isPacketSane(self, message, keycheck=["cmd", "val"], datalimit=1000):
        # TODO: Optimize this fugly mess
        tmp_msg = message
        is_valid_json = False
        is_sane = True
        try:
            if type(tmp_msg) == dict:
                is_valid_json = True
            elif type(tmp_msg) == str:
                tmp_msg = self.json.loads(message)
                is_valid_json = True
        except:
            is_valid_json = True
            is_sane = False
        finally:
            if is_valid_json:
                for key in keycheck:
                    if not key in tmp_msg:
                        if (not "val" in tmp_msg) and (not "code" in tmp_msg):
                            is_sane = False
                if is_sane:
                    if type(tmp_msg["cmd"]) != str:
                        is_sane = False
                    if "id" in tmp_msg:
                        if not (type(tmp_msg["id"]) in [str, dict, int, list]):
                            is_sane = False

                        # Add support for multicast messages
                        if type(tmp_msg["id"]) == list:
                            for entry in tmp_msg["id"]:
                                if not (type(entry) in [str, dict, int]):
                                    is_sane = False

                    if "val" in tmp_msg:
                        origin_type = type(tmp_msg["val"])
                        if not(type(tmp_msg["val"]) in [str, dict, list]):
                            tmp_msg["val"] = str(tmp_msg["val"])
                        if len(tmp_msg["val"]) > datalimit:
                            is_sane = False
                        tmp_msg["val"] = origin_type(tmp_msg["val"])

                    if "name" in tmp_msg:
                        if type(tmp_msg["name"]) != str:
                            is_sane = False
                        if len(tmp_msg["name"]) > datalimit:
                            is_sane = False

                    if "origin" in tmp_msg:
                        if type(tmp_msg["origin"]) != dict:
                            is_sane = False
            return is_sane
