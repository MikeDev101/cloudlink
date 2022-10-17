class CloudCoin:
    def __init__(self, cl):
        self.cl = cl
        self.db = self.cl.db
        self.suit = self.cl.suit
        self.log = self.cl.log
        if not hasattr(self.suit, "CA"):
            raise RuntimeError("CA Not enabled. CC requires CA to be enabled")
        self.CA = self.suit.CA
        self.supporter = self.cl.supporter

        self.supporter.codes.update(
            {
                "NotEnoughCoins": (
                    "I",
                    115,
                    "Your dont have enough coins",
                )
            }
        )

    async def add_coin(self, client, message, listener_detected, listener_id):
        if not self.CA.IsAuthed(client):
            await self.supporter.send_code(
                client,
                "NotLoggedIn",
                listener_detected=listener_detected,
                listener_id=listener_id,
            )
            return

        self.db.users.update_one(
            {
                "username": client.friendly_username,
            },
            {
                "$set": {
                    "coins": self.db.users.find_one(
                        {"username": client.friendly_username}
                    ).get("coins", 0)
                    + int(message["ammount"])
                },
            },
        )
        await self.cl.send_code(
            client,
            "OK",
            listener_detected=listener_detected,
            listener_id=listener_id,
        )

        # tell all clients of user to update coins
        rx_client = self.cl.clients.get_all_with_username(client.friendly_username)
        if not (len(rx_client) == 0):
            await self.cl.send_packet_multicast(
                rx_client,
                cmd="set_coins",
                val={
                    "val": self.db.users.find_one(
                        {"username": client.friendly_username}
                    ).get("coins", 0),
                    "origin": client.id,
                },
                quirk=self.cl.supporter.quirk_update_msg,
                listener_detected=listener_detected,
                listener_id=listener_id,
            )

    async def spend_coins(self, client, message, listener_detected, listener_id):
        if not self.CA.IsAuthed(client):
            await self.cl.send_code(
                client,
                "NotLoggedIn",
                listener_detected=listener_detected,
                listener_id=listener_id,
            )

            return

        if self.db.users.find_one({"username": client.friendly_username}).get(
            "coins", 0
        ) < int(message["ammount"]):
            await self.cl.send_code(
                client,
                "NotEnoughCoins",
                listener_detected=listener_detected,
                listener_id=listener_id,
            )
            return

        self.db.users.update_one(
            {
                "username": client.friendly_username,
            },
            {
                "$set": {
                    "coins": self.db.users.find_one(
                        {"username": client.friendly_username}
                    ).get("coins", 0)
                    - int(message["ammount"])
                }
            },
        )

        await self.cl.send_code(
            client,
            "OK",
            listener_detected=listener_detected,
            listener_id=listener_id,
        )

        # tell all clients of user to update coins
        rx_client = self.cl.clients.get_all_with_username(client.friendly_username)
        if not (len(rx_client) == 0):
            await self.cl.send_packet_multicast(
                rx_client,
                cmd="set_coins",
                val={
                    "val": self.db.users.find_one(
                        {"username": client.friendly_username}
                    ).get("coins", 0),
                    "origin": client.id,
                },
                quirk=self.cl.supporter.quirk_update_msg,
                listener_detected=listener_detected,
                listener_id=listener_id,
            )

    async def send_coins(self, client, message, listener_detected, listener_id):
        if not self.CA.IsAuthed(client):
            await self.cl.send_code(
                client,
                "NotLoggedIn",
                listener_detected=listener_detected,
                listener_id=listener_id,
            )
            return

        other_usr = message["id"]
        if other_usr == client.friendly_username:
            await self.cl.send_code(
                client,
                "OK",
                listener_detected=listener_detected,
                listener_id=listener_id,
            )
            return  # do nothing but send OK to the client

        # check if the user who is sending has enough coins
        if self.db.users.find_one({"username": client.friendly_username}).get(
            "coins", 0
        ) < int(message["ammount"]):
            await self.cl.send_code(
                client,
                "NotEnoughCoins",
                listener_detected=listener_detected,
                listener_id=listener_id,
            )
            return

        # do the coin transfer
        self.db.users.update_one(
            {
                "username": other_usr,
            },
            {
                "$set": {
                    "coins": self.db.users.find_one({"username": other_usr}).get(
                        "coins", 0
                    )
                    + int(message["ammount"])
                }
            },
        )

        self.db.users.update_one(
            {
                "username": client.friendly_username,
            },
            {
                "$set": {
                    "coins": self.db.users.find_one(
                        {"username": client.friendly_username}
                    ).get("coins", 0)
                    - int(message["ammount"])
                }
            },
        )

        await self.cl.send_code(
            client,
            "OK",
            listener_detected=listener_detected,
            listener_id=listener_id,
        )
        # send to the sender that the coins were transferred
        rx_client = self.cl.clients.get_all_with_username(other_usr)
        if not (len(rx_client) == 0):
            await self.cl.send_packet_multicast(
                rx_client,
                cmd="set_coins",
                val={
                    "val": self.db.users.find_one({"username": other_usr}).get(
                        "coins", 0
                    ),
                    "origin": client.id,
                },
                quirk=self.cl.supporter.quirk_update_msg,
                listener_detected=listener_detected,
                listener_id=listener_id,
            )
        rx_client = self.cl.clients.get_all_with_username(client.friendly_username)
        if not (len(rx_client) == 0):
            await self.cl.send_packet_multicast(
                rx_client,
                cmd="set_coins",
                val={
                    "val": self.db.users.find_one(
                        {"username": client.friendly_username}
                    ).get("coins", 0),
                    "origin": client.id,
                },
                quirk=self.cl.supporter.quirk_update_msg,
                listener_detected=listener_detected,
                listener_id=listener_id,
            )
