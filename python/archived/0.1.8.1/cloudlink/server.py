import sys
import logging
from .websocket_server import WebsocketServer
from .supporter import supporter
from .serverRootHandlers import serverRootHandlers
from .serverInternalHandlers import serverInternalHandlers

class server:
    def __init__(self, parentCl, enable_logs):
        # Read the CloudLink version from the parent class
        self.version = parentCl.version

        # Init stuff for the server
        self.userlist = []

        # Rooms system
        self.roomData = {
            "default": []
        }

        self.motd_enable = False
        self.motd_msg = ""
        self.global_msg = ""
        
        # Init modules
        self.supporter = supporter(self, enable_logs)
        self.log = self.supporter.log
        self.serverRootHandlers = serverRootHandlers(self)
        self.serverInternalHandlers = serverInternalHandlers(self)
        
        # Load built-in commands (automatically generates attributes for callbacks)
        self.builtInCommands = []
        self.customCommands = []
        self.disabledCommands = []
        self.usercallbacks = {}
        self.supporter.loadBuiltinCommands()

        # Extra configuration
        self.ipblocklist = [] # Use to block IP addresses
        self.rejectClientMode = False # Set to true to reject future clients until false
        
        # Create API
        self.loadCustomCommands = self.supporter.loadCustomCommands
        self.disableCommands = self.supporter.disableCommands
        self.sendPacket = self.supporter.sendPacket
        self.sendCode = self.supporter.sendCode
        self.linkClientToRooms = self.supporter.linkClientToRooms
        self.unlinkClientFromRooms = self.supporter.unlinkClientFromRooms
        self.getAllUsersInRoom = self.supporter.getAllUsersInRoom
        self.getAllUsersInManyRooms = self.supporter.getAllUsersInManyRooms
        self.getAllRooms = self.supporter.getAllRooms
        self.getAllClientRooms = self.supporter.getAllClientRooms
        self.getUsernames = self.supporter.getUsernames
        self.setClientUsername = self.supporter.setClientUsername
        
        # Create stuff for the callback system
        self.on_packet = self.serverRootHandlers.on_packet
        self.on_connect = self.serverRootHandlers.on_connect
        self.on_close = self.serverRootHandlers.on_close

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

    def setMOTD(self, enable:bool, msg:str):
        self.motd_enable = enable
        self.motd_msg = msg

    def callback(self, callback_id, function):
        # Support older servers which use the old callback system.
        if type(callback_id) == str:
            callback_id = getattr(self, callback_id)
        
        # New callback system.
        if callable(callback_id):
            if callback_id == self.on_packet:
                self.usercallbacks[self.on_packet] = function
            elif callback_id == self.on_connect:
                self.usercallbacks[self.on_connect] = function
            elif callback_id == self.on_close:
                self.usercallbacks[self.on_close] = function
            elif callback_id == self.on_error:
                self.usercallbacks[self.on_error] = function
