from datetime import datetime
import traceback
import sys
import json
from copy import copy

class supporter:
    """
    cloudlink.supporter

    This module provides extended functionality for Cloudlink. This is shared between cloudlink.client and cloudlink.server.
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
        
        # Death to unnecessary if/else trees, long live Python 3.10 switch cases
        match mode:
            case 1:
                setattr(self, "sendPacket", self._sendPacket_server)
                setattr(self, "sendCode", self._sendCode)
            case 2:
                setattr(self, "sendPacket", self._sendPacket_client_async)
            case 3:
                setattr(self, "sendPacket", self._sendPacket_client_noasync)
            case _:
                raise NotImplementedError("Invalid supporter mode")
    
    def paginate_ulist(self, ulist, page_select = 1, pagesize = 30):
        # Mitigate size changed during iteration errors
        tmp_ulist = copy(ulist)
        
        if not(type(tmp_ulist)) in [list, set]:
            raise TypeError
        
        if len(tmp_ulist) == 0:
            return 0, 0, []
        
        if len(tmp_ulist) < pagesize:
            return 1, len(tmp_ulist), tmp_ulist
        
        pages = (len(tmp_ulist) // pagesize)
        tmp_ulist_paginated = []
        for entry in range(pagesize):
            select = entry + (((1 - abs(page_select)) // pagesize) * pagesize)
            tmp_ulist_paginated.append(tmp_ulist[select])
        
        return pages, len(tmp_ulist), tmp_ulist_paginated
    
    async def _sendCode(self, client:dict, code:str, listener_detected:bool = False, listener_id:str = "", extra_data = None):
        message = {
            "cmd": "statuscode",
            "code": self.codes[code]
        }

        if extra_data != None:
            message["val"] = extra_data

        if listener_detected:
            message["listener"] = listener_id

        await client.send(self.json.dumps(message))
    
    def _sendPacket_client_noasync(self, message):
        try:
            self.cloudlink.wss.send(self.json.dumps(message))
        except:
            pass
    
    async def _sendPacket_client_async(self, message):
        try:
            await self.cloudlink.ws_client.send(self.json.dumps(message))
        except:
            pass
    
    async def _sendPacket_server(self, clients, message:dict, listener_detected:bool = False, listener_id:str = "", rooms:list = None, ignore_rooms:bool = False):
        # Mitigate size changed during iteration errors
        clients = copy(clients)
        
        if not type(message) == dict:
            raise TypeError
        
        # Attach listener (if applied to origin message)
        if listener_detected:
            message["listener"] = listener_id

        # Convert clients to set
        if type(clients) == list:
            clients = set(clients)
        elif type(clients) != set:
            clients = set([clients])
        
        # Convert rooms to set
        if type(rooms) == list:
            rooms = set(rooms)
        elif type(rooms) != set:
            rooms = set([rooms])
        
        # Send to all specified clients
        for client in clients:
            if not ignore_rooms:
                for room in rooms:
                    if room == None:
                        room = "default"
                    message["room"] = room
                    if room in list(client.rooms):
                        try:
                            await client.send(self.json.dumps(message))
                        except:
                            pass
            else:
                try:
                    await client.send(self.json.dumps(message))
                except:
                    pass
    
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
            # Check if the function is not already disabled
            if not functionEntry in self.cloudlink.disabledCommands:
                self.cloudlink.disabledCommands.append(functionEntry)
            
            # Prevent modifying private methods, they are not imported anyway
            if (not("__" in functionEntry) and (hasattr(self.cloudlink, functionEntry))): 
                
                # Check if the command is a built-in command
                if functionEntry in self.cloudlink.builtInCommands:
                    self.cloudlink.builtInCommands.remove(functionEntry)
                    delattr(self.cloudlink, str(functionEntry))
                
                # Check if the command is a custom command
                elif functionEntry in self.cloudlink.customCommands:
                    self.cloudlink.customCommands.remove(functionEntry)
                    delattr(self.cloudlink, str(functionEntry))
                
                # Something else
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
    
    def log(self, event, force:bool = False):
        if self.enable_logs or force:
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
        
        # Ignore conversion if the message is already a dictionary, otherwise attempt to convert to JSON
        try:
            if type(tmp_msg) == dict:
                is_valid_json = True
            
            elif type(tmp_msg) == str:
                tmp_msg = self.json.loads(message)
                is_valid_json = True
            
        except:
            is_valid_json = True
            is_sane = False
            
        # Scan the message for syntax, formatting, and datatypes
        finally:
            if is_valid_json:
                
                # Check if the message contains required JSON keys
                for key in keycheck:
                    if not key in tmp_msg:
                        if (not "val" in tmp_msg) and (not "code" in tmp_msg):
                            is_sane = False
                
                # Verify that the packet has the correct datatypes
                if is_sane:
                    if type(tmp_msg["cmd"]) != str:
                        is_sane = False
                    
                    # Check if id is valid
                    if "id" in tmp_msg:
                        if not (type(tmp_msg["id"]) in [str, dict, int, list]):
                            is_sane = False

                        # Add support for multicast messages
                        if type(tmp_msg["id"]) == list:
                            for entry in tmp_msg["id"]:
                                if not (type(entry) in [str, dict, int]):
                                    is_sane = False
                    
                    # Check if payload is valid
                    if "val" in tmp_msg:
                        origin_type = type(tmp_msg["val"])
                        if not(type(tmp_msg["val"]) in [str, dict, list]):
                            tmp_msg["val"] = str(tmp_msg["val"])
                        if len(tmp_msg["val"]) > datalimit:
                            is_sane = False
                        tmp_msg["val"] = origin_type(tmp_msg["val"])
                    
                    # Check if variable names are valid
                    if "name" in tmp_msg:
                        if type(tmp_msg["name"]) != str:
                            is_sane = False
                        if len(tmp_msg["name"]) > datalimit:
                            is_sane = False
                    
                    # Check if client origins are valid
                    if "origin" in tmp_msg:
                        if type(tmp_msg["origin"]) != dict:
                            is_sane = False
                    
                    # Check if relays are valid
                    if "relay" in tmp_msg:
                        if type(tmp_msg["relay"]) != dict:
                            is_sane = False
            return is_sane
