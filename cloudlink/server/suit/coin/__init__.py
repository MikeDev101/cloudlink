class CloudCoin:
    def __init__(self, cl):
        self.cl = cl
        self.db = self.cl.db
        self.suit = self.cl.suit
        self.log = self.cl.log
        if not hasattr(self.suit, "CA"):
            raise RunTimeError("CA Not enabled. CC requires CA to be enabled")
        self.CA = self.suit.CA
        self.supporter = self.cl.supporter

        self.supporter.codes.extend(
            {
                "NotEnoughCoins": (
                    "I",
                    115,
                    "Your dont have enough coins",
                )
            }
        )

    async def add_coins(self, client, message, listener_detected, listener_id, room_id):
        if not self.CA.IsAuthed(client):
            await self.supporter.send_code(
                client,
                "NotLoggedIn",
                listener_detected=listener_detected,
                listener_id=listener_id,
            )
            return

        self.db.update_one(
            {
                "username": client.username,
            },
            {
                "coins": self.db.get_one({"username": client.username}).get("coins", 0)
                + int(message["ammount"])
            },
        )
        self.supporter.send_code(
            client,
            "OK",
            listener_detected=listener_detected,
            listener_id=listener_id,
        )

        # tell all clients of user to update coins
        rx_client = self.cl.users.get_all_with_username(client.username)
        if not (len(rx_client) == 0):
            await self.cl.send_packet(
                rx_client,
                {
                    "cmd": "set_coins",
                    "val": db.get_one({"username": client.username}).get("coins", 0),
                    "origin": client.id,
                },
            )

    async def spend_coins(
        self, client, message, listener_detected, listener_id, room_id
    ):
        if not self.CA.IsAuthed(client):
            await self.cl.send_code(
                client,
                "NotLoggedIn",
                listener_detected=listener_detected,
                listener_id=listener_id,
            )

            return

        if self.db.get_one({"username": client.username}).get("coins", 0) < int(
            message["ammount"]
        ):
            await self.cl.send_code(
                client,
                "NotEnoughCoins",
                listener_detected=listener_detected,
                listener_id=listener_id,
            )
            return

        self.db.update_one(
            {
                "username": client.username,
            },
            {
                "coins": self.db.get_one({"username": client.username}).get("coins", 0)
                - int(message["ammount"])
            },
        )

        await self.cl.send_code(
            client,
            "OK",
            listener_detected=listener_detected,
            listener_id=listener_id,
        )

        # tell all clients of user to update coins
        rx_client = self.cl.users.get_all_with_username(client.username)
        if not (len(rx_client) == 0):
            await self.cl.send_packet(
                rx_client,
                {
                    "cmd": "set_coins",
                    "val": db.get_one({"username": client.username}).get("coins", 0),
                    "origin": client.id,
                },
            )


async def send_coins(self, client, message, listener_detected, listener_id, room_id):
    if not self.CA.IsAuthed(client):
        await self.cl.send_code(
            client,
            "NotLoggedIn",
            listener_detected=listener_detected,
            listener_id=listener_id,
        )
        return

    other_usr = message["id"]
    if other_usr == client.username:
        await self.cl.send_code(
            client,
            "OK",
            listener_detected=listener_detected,
            listener_id=listener_id,
        )
        return  # do nothing but send OK to the client

    # check if the user who is sending has enough coins
    if self.db.get_one({"username": client.username}).get("coins", 0) < int(
        message["ammount"]
    ):
        await self.cl.send_code(
            client,
            "NotEnoughCoins",
            listener_detected=listener_detected,
            listener_id=listener_id,
        )
        return

    # do the coin transfer
    self.db.update_one(
        {
            "username": other_usr,
        },
        {
            "coins": self.db.get_one({"username": other_usr}).get("coins", 0)
            + int(message["ammount"])
        },
    )

    self.db.update_one(
        {
            "username": client.username,
        },
        {
            "coins": self.db.get_one({"username": client.username}).get("coins", 0)
            - int(message["ammount"])
        },
    )

    await self.cl.send_code(
        client,
        "OK",
        listener_detected=listener_detected,
        listener_id=listener_id,
    )
    # send to the sender that the coins were transferred
    rx_client = self.cl.users.get_all_with_username(other_usr)
    if not (len(rx_client) == 0):
        await self.cl.send_packet(
            rx_client,
            {
                "cmd": "set_coins",
                "val": db.get_one({"username": other_usr}).get("coins", 0),
                "origin": client.id,
            },
        )
        rx_client = self.cl.users.get_all_with_username(client.username)
        if not (len(rx_client) == 0):
            await self.cl.send_packet(
                rx_client,
                {
                    "cmd": "set_coins",
                    "val": db.get_one({"username": client.username}).get("coins", 0),
                    "origin": client.id,
                },
            )
