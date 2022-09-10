from .websocket_server import WebsocketServer
from .serverRootHandlers import serverRootHandlers
from .serverInternalHandlers import serverInternalHandlers

class server:
    """
    cloudlink.server

    This is the server mode for Cloudlink. This is a standalone server that supports extra functionality through custom commands or callbacks.
    """

    def __init__(self, parentCl, enable_logs=True):
        # Read the CloudLink version from the parent class
        self.version = parentCl.version

        # Init the server
        self.userlist = []
        self.motd_enable = False
        self.motd_msg = ""
        self.global_msg = ""
        self.roomData = {
            "default": set()
        }
        
        # Init modules
        self.supporter = parentCl.supporter(self, enable_logs, 1)
        self.serverRootHandlers = serverRootHandlers(self)
        self.serverInternalHandlers = serverInternalHandlers(self)
        
        # Load built-in commands (automatically generates attributes for callbacks)
        self.builtInCommands = []
        self.customCommands = []
        self.disabledCommands = []
        self.usercallbacks = {}
        self.supporter.loadBuiltinCommands(self.serverInternalHandlers)

        # Extra configuration
        self.ipblocklist = [] # Use to block IP addresses
        self.rejectClientMode = False # Set to true to reject future clients until false
        
        # Create API
        self.loadCustomCommands = self.supporter.loadCustomCommands
        self.disableCommands = self.supporter.disableCommands
        self.sendPacket = self.supporter.sendPacket
        self.sendCode = self.supporter.sendCode
        self.log = self.supporter.log
        self.callback = self.supporter.callback
        
        # Create callbacks, command-specific callbacks are not needed in server mode
        self.on_packet = self.serverRootHandlers.on_packet
        self.on_connect = self.serverRootHandlers.on_connect
        self.on_close = self.serverRootHandlers.on_close

        self.log("Cloudlink server initialized!")

    def run(self, port=3000, host="127.0.0.1"):
        # Initialize the Websocket Server
        self.log("Cloudlink server starting up now...")
        self.wss = WebsocketServer(host, port)

        # Bind built-in callbacks
        self.wss.set_fn_new_client(self.serverRootHandlers.on_connect)
        self.wss.set_fn_message_received(self.serverRootHandlers.on_packet)
        self.wss.set_fn_client_left(self.serverRootHandlers.on_close)

        # Create attributes
        self.all_clients = self.wss.clients

        # Run the CloudLink server
        self.wss.run_forever()
        self.log("Cloudlink server exiting...")

    # Server API

    def setMOTD(self, enable:bool, msg:str):
        self.motd_enable = enable
        self.motd_msg = msg

    def setClientUsername(self, client, username):
        if type(username) == str:
            if client in self.all_clients:
                if not client.username_set:
                    self.log(f"Setting client {client.id} ({client.full_ip}) username to \"{username}\"...")
                    client.friendly_username = username
                    client.username_set = True
        else:
            raise TypeError

    def createAttrForClient(self, client):
        client.friendly_username = ""
        client.username_set = False
        client.rooms = ["default"]
        client.is_linked = False

    def rejectClient(self, client, reason):
        if client in self.all_clients:
            client.send_close(1000, bytes(reason, encoding='utf-8'))
            self.wss._terminate_client_handler(client)

    def getUserObject(self, identifier):
        # NOT RECOMMENDED - Try to find the client object with a username
        if type(identifier) == str:
            clientIDs = []
            clientObjs = []
            for client in self.all_clients:
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
            for client in self.all_clients:
                clientIDs.append(client.id)
                clientObjs.append(client)
            
            if identifier in clientIDs:
                return clientObjs[clientIDs.index(identifier)]
    
        # UGLY BUT WORKS - Identify client object using the output of supporter.getUserlist / serverInternalHandlers.setid ({"username": "", "id": ""} pairing for clients)
        elif type(identifier) == dict:
            clientIDs = []
            clientObjs = []
            for client in self.all_clients:
                clientIDs.append(client.id)
                clientObjs.append(client)
            
            if identifier["id"] in clientIDs:
                return clientObjs[clientIDs.index(identifier["id"])]
        
        # Unsupported type
        else:
            return TypeError

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
    
    def getUserObjectFromClientObj(self, client):
        if client in self.all_clients:
            if client.username_set:
                return {
                    "username": client.friendly_username, 
                    "id": client.id
                }
    
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
        if room_id in self.roomData:
            return self.roomData[room_id]
        else:
            return []
    
    def getAllRooms(self):
        return list(self.roomData.keys())
    
    def getAllClientRooms(self, client):
        roomlist = set()
        for room in client.rooms:
            roomlist.add(room)
        return roomlist
    
    def linkClientToRooms(self, client, rooms):
        if type(rooms) in [str, list, set]:
            if client in self.all_clients:
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
        if client in self.all_clients: 
            self.log(f"Unlinking client {client.id} ({client.full_ip}) from rooms...")
            # Remove client from all rooms
            self.removeClientFromAllRooms(client)

            # Add client to default room
            client.rooms = ["default"]
            self.roomHandler(1, client, ["default"])

            # Mark as not linked
            client.is_linked = False
    
    def removeClientFromAllRooms(self, client):
        if client in self.all_clients: 
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
        if not room_id in self.roomData:
            self.roomData[room_id] = set()
        
        # Add the client object to the room
        if not client in self.roomData[room_id]:
            self.roomData[room_id].add(client)

    def leaveRoom(self, room_id, client):
        # Check if room exists
        if room_id in self.roomData:
            # Check if client object is in the room
            if client in self.roomData[room_id]:
                self.roomData[room_id].discard(client)
            
            # Automatically remove empty rooms, and prevent accidental deletion of the default room
            if (len(self.roomData[room_id]) == 0) and (room_id != "default"): 
                del self.roomData[room_id]