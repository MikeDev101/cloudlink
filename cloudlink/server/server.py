from .serverRootHandlers import serverRootHandlers
from .serverInternalHandlers import serverInternalHandlers
import copy

class server:
    """
    cloudlink.server

    This is the server mode for Cloudlink. This is a standalone server that supports extra functionality through custom commands or callbacks.
    """

    def __init__(self, parentCl, enable_logs=True):
        # Read the CloudLink version from the parent class
        self.version = parentCl.version
        self.asyncio = parentCl.asyncio
        self.wss = parentCl.ws

        # Init the server
        self.userlist = []
        self.motd_enable = False
        self.motd_msg = ""
        self.global_msg = ""
        self.roomData = {
            "default": set()
        }
        self.all_clients = set()
        self.ws_server = None
        self.id_counter = 0
        
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
        
        # Create default callbacks
        self.on_packet = self.serverRootHandlers.on_packet
        self.on_connect = self.serverRootHandlers.on_connect
        self.on_close = self.serverRootHandlers.on_close
        self.on_direct = self.serverInternalHandlers.direct
        
        # Callbacks for command-specific events
        self.on_direct = self.serverInternalHandlers.direct
        self.on_ulist = self.serverInternalHandlers.ulist
        self.on_statuscode = self.serverInternalHandlers.statuscode
        self.on_setid = self.serverInternalHandlers.setid
        self.on_gmsg = self.serverInternalHandlers.gmsg
        self.on_gvar = self.serverInternalHandlers.gvar
        self.on_pvar = self.serverInternalHandlers.pvar
        self.on_pmsg = self.serverInternalHandlers.pmsg
        self.on_ping = self.serverInternalHandlers.ping

        self.log("Cloudlink server initialized!")
    
    # Server API
    
    def run(self, port=3000, host="127.0.0.1"):
        # Initialize the Websocket Server
        self.log("Cloudlink server is starting up now...")
        try:
            self.ws_server = self.wss.serve(self.__handler__, host, port)
            loop = self.asyncio.get_event_loop()
            loop.run_until_complete(self.__run__())
            loop.close()
        except KeyboardInterrupt:
            # Make keyboard interrupts silent
            pass
        self.log("Cloudlink server shutting down...")
    
    async def stop(self):
        if self.ws_server.is_serving():
            self.ws_server.close()
            await self.ws_server.wait_close()

    def setMOTD(self, enable:bool, msg:str):
        self.motd_enable = enable
        self.motd_msg = msg

    def setClientUsername(self, client, username):
        if type(username) == str:
            all_clients = self.all_clients.copy()
            if client in all_clients:
                if not client.username_set:
                    self.log(f"Setting client {client.id} ({client.full_ip}) username to \"{username}\"...")
                    client.friendly_username = username
                    client.username_set = True
        else:
            raise TypeError
    
    async def rejectClient(self, client, reason):
        all_clients = self.all_clients.copy()
        if client in all_clients:
            client.rejected = True
            await client.close(1000, reason)

    def getUserObject(self, identifier, force = False):
        all_clients = self.all_clients.copy()
        # NOT RECOMMENDED - Try to find the client object with a username
        if type(identifier) == str:
            clientIDs = []
            clientObjs = []
            for client in all_clients:
                clientIDs.append(client.friendly_username)
                clientObjs.append(client)
            
            if identifier in clientIDs:
                # Sort
                selectionTmp = []
                for read in clientIDs:
                    if read == identifier:
                        selectionTmp.append(read)
                # Return result
                if (len(selectionTmp) > 1) and not force:
                    return LookupError # There are more than one clients with that username
                elif len(selectionTmp) == 0:
                    return None # No client found
                else:
                    return clientObjs[clientIDs.index(identifier)]

        # BEST PRACTICE - Identify client object using it's websocket object number
        elif type(identifier) == int:
            for client in all_clients:
                if identifier == client.id:
                    return client
    
        # UGLY BUT WORKS - Identify client object using the output of supporter.getUserlist / serverInternalHandlers.setid ({"username": "", "id": ""} pairing for clients)
        elif type(identifier) == dict:
            for client in all_clients:
                if identifier["id"] == client.id:
                    return client
        
        # Unsupported type
        else:
            return TypeError
    
    def selectMultiUserObjects(self, identifiers:list, rooms:list = ["default"], force:bool = False):
        # Implement multicast support
        objList = []
        if type(identifiers) == list:
            for client in identifiers:
                obj = self.getUserObject(client, force)
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
        all_clients = self.all_clients.copy()
        if client in all_clients:
            if client.username_set:
                return {
                    "username": client.friendly_username, 
                    "id": client.id
                }
            else:
                return None
    
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
        tmp_roomData = copy.copy(self.roomData)
        if room_id in tmp_roomData:
            return tmp_roomData[room_id]
        else:
            return []
    
    def getAllRooms(self):
        tmp_roomData = copy.copy(self.roomData)
        return list(tmp_roomData.keys())
    
    def getAllClientRooms(self, client):
        roomlist = set()
        for room in client.rooms:
            roomlist.add(room)
        return roomlist
    
    def linkClientToRooms(self, client, rooms):
        if type(rooms) in [str, list, set]:
            all_clients = self.all_clients.copy()
            if client in all_clients:
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
        all_clients = self.all_clients.copy()
        if client in all_clients: 
            self.log(f"Unlinking client {client.id} ({client.full_ip}) from rooms...")
            # Remove client from all rooms
            self.removeClientFromAllRooms(client)

            # Add client to default room
            client.rooms = ["default"]
            self.roomHandler(1, client, ["default"])

            # Mark as not linked
            client.is_linked = False
    
    def removeClientFromAllRooms(self, client):
        all_clients = self.all_clients.copy()
        if client in all_clients: 
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
        tmp_roomData = copy.copy(self.roomData)
        
        if not room_id in tmp_roomData:
            self.roomData[room_id] = set()
            tmp_roomData[room_id] = set()
        
        # Add the client object to the room
        if not client in tmp_roomData[room_id]:
            self.roomData[room_id].add(client)

    def leaveRoom(self, room_id, client):
        # Check if room exists
        tmp_roomData = copy.copy(self.roomData)
        
        if room_id in tmp_roomData:
            # Check if client object is in the room
            if client in tmp_roomData[room_id]:
                self.roomData[room_id].discard(client)
                tmp_roomData[room_id].discard(client)
            
            # Automatically remove empty rooms, and prevent accidental deletion of the default room
            if (len(tmp_roomData[room_id]) == 0) and (room_id != "default"): 
                del self.roomData[room_id]
    
    # Async components that are required to make the server work
    
    async def __run__(self):
        # Init the async server
        self.future = self.asyncio.Future()
        async with self.ws_server:
            self.log("Cloudlink server is ready to accept connections!")
            await self.future # Run the server
    
    async def __handler__(self, websocket):
        # Add client to the server
        self.all_clients.add(websocket)
        
        # Create attributes for the client
        websocket.friendly_username = ""
        websocket.username_set = False
        websocket.rooms = ["default"]
        websocket.is_linked = False
        websocket.id = self.id_counter
        websocket.rejected = False
        
        self.id_counter += 1
        
        # Get the IP address of client
        if "x-forwarded-for" in websocket.request_headers:
            websocket.full_ip = websocket.request_headers.get("x-forwarded-for")
        elif "cf-connecting-ip" in websocket.request_headers:
            websocket.full_ip = websocket.request_headers.get("cf-connecting-ip")
        else:
            if type(websocket.remote_address) == tuple:
                websocket.full_ip = str(websocket.remote_address[0])
            else:
                websocket.full_ip = websocket.remote_address
        
        # Handle the connection
        await self.serverRootHandlers.on_connect(websocket)
        try:
            async for message in websocket:
                await self.serverRootHandlers.on_packet(websocket, message)
        except self.wss.exceptions.ConnectionClosedError:
            pass
        except Exception as e:
            self.supporter.log(f"Async client exception: {e}")
        
        # Shutdown the connection
        finally:
            if not websocket.rejected:
                await self.serverRootHandlers.on_close(websocket, websocket.close_code, websocket.close_reason)
            self.all_clients.remove(websocket)