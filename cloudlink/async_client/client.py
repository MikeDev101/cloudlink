from .clientRootHandlers import clientRootHandlers
from .clientInternalHandlers import clientInternalHandlers

class client:
    """
    cloudlink.client (Async version)

    This is the client mode for Cloudlink. You can connect to a Cloudlink server and send/receive packets like a Scratch client would. This module simplifies the Cloudlink protocol for Python.
    """

    def __init__(self, parentCl, enable_logs=True):
        # Read the CloudLink version from the parent class
        self.version = parentCl.version
        self.asyncio = parentCl.asyncio
        self.wss = parentCl.ws

        # Init the client
        self.motd_msg = ""
        self.sever_version = ""
        self.ip_address = ""
        self.motd_msg = ""
        self.userlist = {}
        self.myClientObject = {}
        self.ws_client = None

        self.linkStatus = 0
        self.failedToConnect = False
        self.connectionLost = False
        
        # Init modules
        self.supporter = parentCl.supporter(self, enable_logs, 2)
        self.clientRootHandlers = clientRootHandlers(self)
        self.clientInternalHandlers = clientInternalHandlers(self)
        
        # Load built-in commands (automatically generates attributes for callbacks)
        self.builtInCommands = []
        self.customCommands = []
        self.disabledCommands = []
        self.usercallbacks = {}
        self.supporter.loadBuiltinCommands(self.clientInternalHandlers)
        
        # Create API
        self.loadCustomCommands = self.supporter.loadCustomCommands
        self.disableCommands = self.supporter.disableCommands
        self.sendPacket = self.supporter.sendPacket
        self.log = self.supporter.log
        self.callback = self.supporter.callback
        
        # Create default callbacks
        self.usercallbacks = {}
        self.on_packet = self.clientRootHandlers.on_packet
        self.on_connect = self.clientRootHandlers.on_connect
        self.on_close = self.clientRootHandlers.on_close
        self.on_error = self.clientRootHandlers.on_error

        # Callbacks for command-specific events
        self.on_direct = self.clientInternalHandlers.direct
        self.on_version = self.clientInternalHandlers.server_version
        self.on_motd = self.clientInternalHandlers.motd
        self.on_ip = self.clientInternalHandlers.client_ip
        self.on_ulist = self.clientInternalHandlers.ulist
        self.on_statuscode = self.clientInternalHandlers.statuscode
        self.on_gmsg = self.clientInternalHandlers.gmsg
        self.on_gvar = self.clientInternalHandlers.gvar
        self.on_pvar = self.clientInternalHandlers.pvar
        self.on_pmsg = self.clientInternalHandlers.pmsg
        self.on_ping = self.clientInternalHandlers.ping

        self.log("Cloudlink async client initialized!")
    
    # Client API
    
    def run(self, ip="ws://127.0.0.1:3000/"):
        # Initialize the Websocket Server
        self.log("Cloudlink client is starting up now...")
        try:
            self.asyncio.run(self.__run__(ip))
        except KeyboardInterrupt:
            # Make keyboard interrupts silent
            pass
        self.log("Cloudlink client shutting down...")
    
    async def stop(self):
        if self.ws_client.open:
            self.log("Client disconnecting...")
            self.ws_client.close()
            await self.ws_client.wait_closed()
    
    async def setUsername(self, username:str):
        if self.ws_client.open:
            msg = {"cmd": "setid", "val": username, "listener": "username_set"}
            await self.cloudlink.sendPacket(msg)

    async def getUserlist(self, listener:str = None):
        if self.ws_client.open:
            msg = {"cmd": "ulist", "val": ""}
            if listener:
                msg["listener"] = listener
            await self.cloudlink.sendPacket(msg)
    
    async def linkToRooms(self, rooms:list = ["default"], listener:str = None):
        if self.ws_client.open:
            msg = {"cmd": "link", "val": rooms}
            if listener:
                msg["listener"] = listener
            await self.cloudlink.sendPacket(msg)
    
    async def unlinkFromRooms(self, listener:str = None):
        if self.ws_client.open:
            msg = {"cmd": "unlink", "val": ""}
            if listener:
                msg["listener"] = listener
            await self.cloudlink.sendPacket(msg)

    async def sendDirect(self, message:any, username:str = None, listener:str = None):
        if self.ws_client.open:
            msg = {"cmd": "direct", "val": message}
            if listener:
                msg["listener"] = listener
            if username:
                msg["id"] = username
            await self.cloudlink.sendPacket(msg)
    
    async def sendCustom(self, cmd:str, message:any, username:str = None, listener:str = None):
        if self.ws_client.open:
            msg = {"cmd": cmd, "val": message}
            if listener:
                msg["listener"] = listener
            if username:
                msg["id"] = username
            await self.cloudlink.sendPacket(msg)
    
    async def sendPing(self, dummy_payload:any = "", username:str = None, listener:str = None):
        if self.ws_client.open:
            msg = {"cmd": "ping", "val": dummy_payload}
            if listener:
                msg["listener"] = listener
            if username:
                msg["id"] = username
            await self.cloudlink.sendPacket(msg)
    
    async def sendGlobalMessage(self, message:any, listener:str = None):
        if self.ws_client.open:
            msg = {"cmd": "gmsg", "val": message}
            if listener:
                msg["listener"] = listener
            await self.cloudlink.sendPacket(msg)
    
    async def sendPrivateMessage(self, message:any, username:str = "", listener:str = None):
        if self.ws_client.open:
            msg = {"cmd": "pmsg", "val": message, "id": username}
            if listener:
                msg["listener"] = listener
            await self.cloudlink.sendPacket(msg)

    async def sendGlobalVariable(self, var_name:str, var_value:any, listener:str = None):
        if self.ws_client.open:
            msg = {"cmd": "gvar", "val": var_value, "name": var_name}
            if listener:
                msg["listener"] = listener
            await self.cloudlink.sendPacket(msg)
    
    async def sendPrivateVariable(self, var_name:str, var_value:any, username:str = "", listener:str = None):
        if self.ws_client.open:
            msg = {"cmd": "pvar", "val": var_value, "name": var_name, "id": username}
            if listener:
                msg["listener"] = listener
            await self.cloudlink.sendPacket(msg)
    
    # Async component that is required to make the client work
    
    async def __run__(self, ip):
        # Init the async client
        self.log("Client is connecting...")
        self.linkStatus = 1
        async with self.wss.connect(ip) as websocket:
            self.ws_client = websocket
            try:
                await self.clientRootHandlers.on_connect()
                while websocket.open:
                    try:
                        message = await websocket.recv()
                        await self.clientRootHandlers.on_packet(message)
                    except Exception as e:
                        await self.clientRootHandlers.on_error(e)
            except self.wss.ConnectionClosed:
                pass
            except Exception as e:
                self.log(f"Exception: {e}")
            finally:
                await self.clientRootHandlers.on_close(websocket.close_code, websocket.close_reason)