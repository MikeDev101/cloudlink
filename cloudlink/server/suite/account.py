
class Account:
    def __init__(self, homeserver_client):
        self.wss = homeserver_client
        self.wss.bind_event(self.statuscode, self.statuscode)
        self.importer_ignore_functions = [self.statuscode]
        self.waiting_clients = {}


    # client methods
    async def statuscode(self, message, listener):
        if listener not in self.waiting_clients: return

        client = self.waiting_clients[listener]
        del self.waiting_clients[listener]

        human_ok, machine_ok = self.supporter.generate_statuscode("OK")

        if not ((message["code"] == human_ok) or (message["code_id"] == machine_ok)):
            await self.wss.server.send_packet_unicast(client, "statuscode", val={"code": message["code"], "code_id": message["code_id"]}, quirk=self.wss.server.supporter.quirk_update_msg, listener=listener)
            return

        self.wss.server.set_client_username(message['username'])
        await self.wss.server.send_code(client, "OK", extra_data={"username": message['username']})
        

    # server methods
    async def login(self, client, message, listener):
        if "userid" not in message:
            await self.wss.server.send_code(client, "Syntax", extra_data={"key":"userid"}, listener=listener)
            return 

        if "user_token" not in message:
            await self.wss.server.send_code(client, "Syntax", extra_data={"key":"user_token"}, listener=listener)
            return 

        # get data out for simplicity
        userid = message['userid']
        user_token = message['user_token']

        await self.wss.send_packet(cmd="Server_LogClientIn", val=message, quirk=self.wss.server.supporter.quirk_update_msg, listener=f"{userid}")
        self.waiting_clients[userid] = {"c":client, "l": listener}


