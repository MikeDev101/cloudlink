from cgitb import enable
from datetime import datetime
import traceback
import sys
import json

class supporter:
    """
    This module provides basic functionality for Cloudlink.
    """

    def __init__(self, cloudlink, enable_logs:bool):
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
        }
    
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

    def sendPacket(self, clients, message:dict, listener_detected:bool = False, listener_id:str = "", rooms:list = None):
        if type(message) == dict:
            if self.isPacketSane(message, ["cmd"]):
                # Attach listener (if applied to origin message)
                if listener_detected:
                    message["listener"] = listener_id

                # Send the message (support for multicast)
                if type(clients) == dict:
                    clients = [clients]
                for client in clients:
                    if rooms in [None, ["default"]]:
                        if "default" in self.readAttrFromClient(client)["rooms"]:
                            self.cloudlink.wss.send_message(client, self.json.dumps(message))
                    else:
                        for room in rooms:
                            if room in self.readAttrFromClient(client)["rooms"]:
                                message["room"] = room
                                self.cloudlink.wss.send_message(client, self.json.dumps(message))

    def rejectClient(self, client, reason):
        if client in self.cloudlink.all_clients:
            client["handler"].send_close(1000, bytes(reason, encoding='utf-8'))
            self.cloudlink.wss._terminate_client_handler(client["handler"])

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

    def loadCustomCommands(self, classes):
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
    
    def loadBuiltinCommands(self):
        # Get an array of attributes from self.serverInternalHandlers
        classFunctions = dir(self.cloudlink.serverInternalHandlers)
        for functionEntry in classFunctions:
            # Check if a function within self.serverInternalHandlers is a private function
            if (not("__" in functionEntry) and (not(hasattr(self.cloudlink, functionEntry)))): 
                try:
                    self.cloudlink.builtInCommands.append(str(functionEntry))
                    setattr(self.cloudlink, str(functionEntry), getattr(self.cloudlink.serverInternalHandlers, str(functionEntry)))
                except:
                    self.log(f"An exception has occurred whilst loading a built-in command: {self.full_stack()}")

    def getUsernames(self, rooms:list = ["default"]):
        userlist = []
        for client in self.cloudlink.all_clients:
            clientAttrs = self.readAttrFromClient(client)
            clientId = {
                "username": clientAttrs["friendly_username"],
                "id": client['id']
            }
            for room in rooms:
                if room in clientAttrs["rooms"]:
                    if clientAttrs["username_set"]:
                        if not clientId in userlist:
                            userlist.append(clientId)
        return userlist

    def getUserObjectFromClientObj(self, client):
        if client in self.cloudlink.all_clients:
            clientAttrs = self.readAttrFromClient(client)
            if clientAttrs["username_set"]:
                return {
                    "username": clientAttrs["friendly_username"], 
                    "id": client['id']
                }

    def selectMultiUserObjects(self, identifiers:list):
        # Implement multicast support
        objList = []
        if type(identifiers) == list:
            for client in identifiers:
                obj = self.getUserObject(client)
                if not(obj in [TypeError, LookupError, None]):
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
                clientIDs.append(self.readAttrFromClient(client)["friendly_username"])
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
                clientIDs.append(client["id"])
                clientObjs.append(client)
            
            if identifier in clientIDs:
                return clientObjs[clientIDs.index(identifier)]
    
        # UGLY BUT WORKS - Identify client object using the output of supporter.getUserlist / serverInternalHandlers.setid ({"username": "", "id": ""} pairing for clients)
        elif type(identifier) == dict:
            clientIDs = []
            clientObjs = []
            for client in self.cloudlink.all_clients:
                clientIDs.append(client["id"])
                clientObjs.append(client)
            
            if identifier["id"] in clientIDs:
                return clientObjs[clientIDs.index(identifier["id"])]
        
        # Unsupported type
        else:
            return TypeError

    def generateClientString(self, client):
        tmp_client = client.copy()
        if type(tmp_client["address"]) == tuple:
            tmp_client["address"] = f"{tmp_client['address'][0]}:{tmp_client['address'][1]}"
        return str(f"__client-{tmp_client['id']}-{tmp_client['address']}__")

    def getFriendlyClientIP(self, client):
        tmp_client = client.copy()
        if type(tmp_client["address"]) == tuple:
            tmp_client["address"] = tmp_client['address'][0]
        return tmp_client["address"]

    def getClientObjFromUsername(self, username):
        return self.getUserObject(username)

    def createAttrForClient(self, client):
        attrstring = self.generateClientString(client)
        if not(hasattr(self.cloudlink, attrstring)):
            setattr(self.cloudlink, attrstring, {
                "friendly_username": "",
                "username_set": False,
                "rooms": ["default"],
                "is_linked": False
            })
            return True
        else:
            return False

    def deleteAttrForClient(self, client):
        attrstring = self.generateClientString(client)
        if hasattr(self.cloudlink, attrstring):
            delattr(self.cloudlink, attrstring)
            return True
        else:
            return False

    def readAttrFromClient(self, client):
        attrstring = self.generateClientString(client)
        if hasattr(self.cloudlink, attrstring):
            return getattr(self.cloudlink, attrstring)
        else:
            return {}

    def writeAttrToClient(self, client, key, data):
        attrstring = self.generateClientString(client)
        if hasattr(self.cloudlink, attrstring):
            tmp_data = getattr(self.cloudlink, attrstring)
            tmp_data[key] = data
            setattr(self.cloudlink, attrstring, tmp_data)
            return True
        else:
            return False

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
                        if type(tmp_msg["val"]) == int:
                            tmp_msg["val"] = str(tmp_msg["val"])
                        if len(tmp_msg["val"]) > datalimit:
                            is_sane = False

                    if "name" in tmp_msg:
                        if type(tmp_msg["name"]) != str:
                            is_sane = False
                        if len(tmp_msg["name"]) > datalimit:
                            is_sane = False

                    if "origin" in tmp_msg:
                        if type(tmp_msg["origin"]) != dict:
                            is_sane = False
            return is_sane