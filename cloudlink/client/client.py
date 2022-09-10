import websocket as WebsocketClient
from .clientRootHandlers import clientRootHandlers
from .clientInternalHandlers import clientInternalHandlers

class client:
    def __init__(self, parentCl, enable_logs=True):
        # Read the CloudLink version from the parent class
        self.version = parentCl.version

        # Init the client
        self.motd_msg = ""
        self.sever_version = ""
        self.ip_address = ""
        self.motd_msg = ""
        self.userlist = {}
        self.myClientObject = {}

        self.linkStatus = 0
        self.failedToConnect = False
        self.connectionLost = False
        self.connected = False
        
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
        self.sendCode = self.supporter.sendCode
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

        self.log("Cloudlink client initialized!")
    
    def run(self, ip="ws://127.0.0.1:3000/"):
        # Initialize the Websocket client
        self.log("Cloudlink client starting up now...")
        self.wss = WebsocketClient.WebSocketApp(
            ip,
            on_message = self.clientRootHandlers.on_packet,
            on_error = self.clientRootHandlers.on_error,
            on_open = self.clientRootHandlers.on_connect,
            on_close = self.clientRootHandlers.on_close
        )

        # Run the CloudLink client
        self.linkStatus = 1
        self.wss.run_forever()
        self.log("Cloudlink client exiting...")

    def stop(self):
        if self.connected:
            self.linkStatus = 3
            self.log("Cloudlink client disconnecting...")
            self.wss.close()

    # Client API

    def setUsername(self, username:str):
        if self.connected:
            msg = {"cmd": "setid", "val": username, "listener": "username_set"}
            self.cloudlink.sendPacket(msg)

    def getUserlist(self, listener:str = None):
        if self.connected:
            msg = {"cmd": "ulist", "val": ""}
            if listener:
                msg["listener"] = listener
            self.cloudlink.sendPacket(msg)
    
    def linkToRooms(self, rooms:list = ["default"], listener:str = None):
        if self.connected:
            msg = {"cmd": "link", "val": rooms}
            if listener:
                msg["listener"] = listener
            self.cloudlink.sendPacket(msg)
    
    def unlinkFromRooms(self, listener:str = None):
        if self.connected:
            msg = {"cmd": "unlink", "val": ""}
            if listener:
                msg["listener"] = listener
            self.cloudlink.sendPacket(msg)

    def sendDirect(self, message:str, username:str = None, listener:str = None):
        if self.connected:
            msg = {"cmd": "direct", "val": message}
            if listener:
                msg["listener"] = listener
            if username:
                msg["id"] = username
            self.cloudlink.sendPacket(msg)
    
    def sendCustom(self, cmd:str, message:str, username:str = None, listener:str = None):
        if self.connected:
            msg = {"cmd": cmd, "val": message}
            if listener:
                msg["listener"] = listener
            if username:
                msg["id"] = username
            self.cloudlink.sendPacket(msg)
    
    def sendPing(self, dummy_payload:str = "", username:str = None, listener:str = None):
        if self.connected:
            msg = {"cmd": "ping", "val": dummy_payload}
            if listener:
                msg["listener"] = listener
            if username:
                msg["id"] = username
            self.cloudlink.sendPacket(msg)
    
    def sendGlobalMessage(self, message:str, listener:str = None):
        if self.connected:
            msg = {"cmd": "gmsg", "val": message}
            if listener:
                msg["listener"] = listener
            self.cloudlink.sendPacket(msg)
    
    def sendPrivateMessage(self, message:str, username:str = "", listener:str = None):
        if self.connected:
            msg = {"cmd": "pmsg", "val": message, "id": username}
            if listener:
                msg["listener"] = listener
            self.cloudlink.sendPacket(msg)

    def sendGlobalVariable(self, var_name:str, var_value:str, listener:str = None):
        if self.connected:
            msg = {"cmd": "gvar", "val": var_value, "name": var_name}
            if listener:
                msg["listener"] = listener
            self.cloudlink.sendPacket(msg)
    
    def sendPrivateVariable(self, var_name:str, var_value:str, username:str = "", listener:str = None):
        if self.connected:
            msg = {"cmd": "pvar", "val": var_value, "name": var_name, "id": username}
            if listener:
                msg["listener"] = listener
            self.cloudlink.sendPacket(msg)