from cloudlink.async_client import client
import sys

class HomeServerConnection(client):
    def __init__(self, server):
       self.server =  server
       self.server.supporter.disable_methods(["setid"])
       self.server_username = ""
       client.__init__(self, server.parent, async_client=True)

       self.bind_event(self.on_connect, self.on_connect)
       self.bind_event(self.statuscode, self.hs_statuscode)

    def run(self, server_username, server_password, ip: str = "ws://127.0.0.1:3000/"):
        self.loop = self.asyncio.get_event_loop()
        self.asyncio.create_task(self.__session__(ip))
        self.server_username = server_username
        self.server_password = server_password

    async def  on_connect(self):
        await self.send_packet(cmd="login", listener="HomeServerConnection", val={"username": self.server_username, "password": self.server_password}, quirk=self.server.supporter.quirk_update_msg)
        await self.send_packet(cmd="RegisterServerAccount")
        
    async def hs_statuscode(self, message, listener):
        human_ok, machine_ok = self.supporter.generate_statuscode("OK")             

        match listener:
           case "HomeServerConnection":
               if not ((message["code"] == human_ok) or (message["code_id"] == machine_ok)):
                  self.server.log_critical("Cant Connect to home Server\n  Human Status: {0} Machine Status: {1} ".format(message["code_id"], message["code"]))
                
               else:
                  self.server.log_info("Connected to home server")
            