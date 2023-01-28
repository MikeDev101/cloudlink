from cloudlink.async_client import client, events
from cloudlink.supporter import supporter
from cloudlink import cloudlink
import sys
class _: 
    supporter = supporter
    version = cloudlink.version

class HomeServerConnection(client):
    def __init__(self, server):
       super().__init__(_, False)
       self.server =  server
       self.server.supporter.disable_methods(["setid"])
       self.server_username = ""
       
       self.ssuporter = self.server.supporter

       self.bind_event(events.on_connect, self._on_connect) #type: ignore
       self.bind_event(self.statuscode, self.hs_statuscode) #type: ignore

    async def run(self, server_username, server_password, ip: str = "ws://127.0.0.1:3000/"):
        
        self.server_username = server_username
        self.server_password = server_password
        await self.__session__(ip)

    async def  _on_connect(self):
        await self.send_packet(cmd="login", listener="HomeServerConnection", val={"username": self.server_username, "password": self.server_password}, quirk=self.server.supporter.quirk_update_msg)
        await self.send_packet(cmd="RegisterServerAccount", val="")
        
    async def hs_statuscode(self, message, listener):
        human_ok, machine_ok = self.supporter.generate_statuscode("OK")             

        match listener:
           case "HomeServerConnection":
               if not ((message["code"] == human_ok) or (message["code_id"] == machine_ok)):
                  self.server.log_critical("Cant Connect to home Server\n  Human Status: {0} Machine Status: {1} ".format(message["code_id"], message["code"]))
                
               else:
                  self.server.log_info("Connected to home server")
    @staticmethod
    def statuscode():
        pass
            