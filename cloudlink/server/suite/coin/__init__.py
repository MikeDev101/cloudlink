class CloudCoin:
    def __init__(self, cl, account_username, account_password):
        self.suit = cl.suit
        self.cl = cl
        self.home_server_con = self.cl.parrent.client(
            async_client=True, logs=self.cl.enable_logs
        )
        self.home_server_con.bind_event(
            self.home_server_con.statuscode, self._handle_statuscode
        )
        self.home_server_con.bind_event(
            self.home_server_con.events.on_connect, self._on_home_connect
        )

        self.secret = None
        self.refresh_token = None
        self.token = None
        self.waiting_for_status = {}
        self.auth_done = False
        self.account_username = account_username
        self.account_password = account_password

    async def _handle_statuscode(self, statuscode, message):
        if "listener" in message:
            # internal cbs lmao
            cb = message["listener"]
            if cb == "LoginPart1":
                if not message["status_id"] == 100:
                    self.cl.error("account login failed:" + message["status"])
                    return

                self.refresh_token = message["refresh_token"]
                self.token = message["token"]

                if not self.auth_done:
                    self.cl.log("Logged in")
                    lp = asyncio.get_event_loop()
                    self._refresh_task = asyncio.call_soon(self.refresh_task, lp)

                    self.auth_done = True
                    await self.home_server_con.send_packet(
                        quirk=self.cl.supporter.quirk_update_msg,
                        cmd="login_project",
                        listener="LoginPart2",
                    )
                else:
                    self.cl.log("Refreshed auth")
            elif cb == "LoginPart2":
                if not message["status_id"] == 200:
                    self.cl.error("account login failed:" + message["status"])
                    return
                self.secret = message["secret"]

        await self.cl.send_code(
            self.waiting_for_status[message["user"]]["client"],
            message["code"],
            **self.waiting_for_status[message["user"]]["listener"],
        )
        del self.waiting_for_status[message["user"]]

    async def _login_loop(self):
        while True:
            await asyncio.sleep(2400 - 60)
            await self.home_server_con.send_packet(
                quirk=self.cl.supporter.quirk_update_msg,
                cmd="refresh_auth",
                listener="LoginPart1",
                val={"refresh_token": self.refresh_token},
            )

    async def _on_home_connect(self):
        self.home_server_con.send_packet(
            cmd="login",
            listener="LoginPart1",
            val={"username": self.account_username, "password": self.account_password},
            quirk=self.cl.supporter.quirk_update_msg,
        )

    async def transfer(
        self,
        client,
        message,
        listener_detected,
        listener_id,
    ):
        del message["cmd"]
        message["user"] = client.frendly_username

        self.waiting_for_status[client.frendly_username] = {
            "client": client,
            "listener": {
                "listener_detected": listener_detected,
                "listener_id": listener_id,
            },
        }

        self.home_server_con.send_packet(
            quirk=self.cl.supporter.quirk_update_msg,
            cmd="transfer_to_project",
            val=message,
            listener_detected=listener_detected,
            listener_id=listener_id,
        )
