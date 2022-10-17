class CloudDisk:
    def __init__(self, cl):
        self.cl = cl
        self.suporter = self.cl.supporter
        self.db = self.cl.db
        self.CA = self.cl.suit.CA
        self.suporter.codes.update(
            {
                "StoreageFull": ("E", 117, "Storage is full"),
                "StoreageNotFound": ("E", 118, "Storage not found"),
            }
        )

    async def create_disk(self, client, message, listener_detected, listener_id):
        if not self.CA.IsAuthed(client):
            await self.cl.send_code(
                client,
                "NotLoggedIn",
                listener_detected=listener_detected,
                listener_id=listener_id,
            )
            return

        usr = self.db.users.find_one({"username": client.friendly_username})

        if len(usr.get("disks", [])) > 10:
            await self.cl.send_code(
                client,
                "StorageFull",
                listener_detected=listener_detected,
                listener_id=listener_id,
            )
            return

        self.db.users.update_one(
            {"username": client.friendly_username},
            {
                "$push": {
                    "disks": [
                        {
                            "data": message["val"],
                        }
                    ]
                }
            },
        )
        await self.cl.send_code(
            client, "OK", listener_detected=listener_detected, listener_id=listener_id
        )

        rx_client = self.cl.clients.get_all_with_username(client.friendly_username)
        if not (len(rx_client) == 0):
            await self.cl.send_packet(
                rx_client,
                cmd="update_disks",
                val={
                    "val": len(usr.get("disks", [])) + 1,
                    "origin": client.id,
                },
                listener_detected=listener_detected,
                listener_id=listener_id,
                quirk=self.cl.supporter.quirk_update_msg,
            )

    async def delete_disk(self, client, message, listener_detected, listener_id):
        if not self.CA.IsAuthed(client):
            await self.cl.send_code(
                client,
                "NotLoggedIn",
                listener_detected=listener_detected,
                listener_id=listener_id,
            )
            return
        if not "disk_id" in message:
            await self.cl.send_code(
                client,
                "Syntax",
                listener_detected=listener_detected,
                listener_id=listener_id,
            )
            return

        usr = self.db.users.find_one({"username": client.friendly_username})
        if len(usr.get("disks", [])) < message["disk_id"]:
            await self.cl.send_code(
                client,
                "DiskNotFound",
                listener_detected=listener_detected,
                listener_id=listener_id,
            )
            return
            self.db.users.update_one(
                {"username": client.friendly_username},
                {
                    "$pull": {
                        "disks": message["disk_id"],
                    }
                },
            )

        await self.cl.send_code(
            client, "OK", listener_detected=listener_detected, listener_id=listener_id
        )

        rx_client = self.cl.clients.get_all_with_username(client.friendly_username)
        if not (len(rx_client) == 0):
            await self.cl.send_packet_multicast(
                rx_client,
                cmd="update_disks",
                val={
                    "val": len(usr.get("disks", [])) - 1,
                    "origin": client.id,
                },
                quirk=self.cl.supporter.quirk_update_msg,
                listener_detected=listener_detected,
                listener_id=listener_id,
            )

        async def get_disk(self, client, message, listener_detected, listener_id):
            if not self.CA.IsAuthed(client):
                await self.cl.send_code(
                    client,
                    "NotLoggedIn",
                    listener_detected=listener_detected,
                    listener_id=listener_id,
                )
                return
            if not "disk_id" in message:
                await self.cl.send_code(
                    client,
                    "Syntax",
                    listener_detected=listener_detected,
                    listener_id=listener_id,
                )
                return
            usr = self.db.users.find_one({"username": client.friendly_username})
            if len(usr.get("disks", [])) < message["disk_id"]:
                await self.cl.send_code(
                    client,
                    "DiskNotFound",
                    listener_detected=listener_detected,
                    listener_id=listener_id,
                )
                return

            await self.cl.send_code(
                client,
                "OK",
                extra_data={
                    "disk": {
                        "id": message["disk_id"],
                        "data": usr.get("disks", [])[message["disk_id"]]["content"],
                    }
                },
                listener_detected=listener_detected,
                listener_id=listener_id,
            )

    async def update_disk(self, client, message, listener_detected, listener_id):
        if not self.CA.IsAuthed(client):
            await self.cl.send_code(
                client,
                "NotLoggedIn",
                listener_detected=listener_detected,
                listener_id=listener_id,
            )
            return
        if not "disk_id" in message or not "val" in message:
            await self.cl.send_code(
                client,
                "Syntax",
                listener_detected=listener_detected,
                listener_id=listener_id,
            )
            return

        usr = self.db.users.find_one({"username": client.friendly_username})
        if len(usr.get("disks", [])) < message["disk_id"]:
            await self.cl.send_code(
                client,
                "DiskNotFound",
                listener_detected=listener_detected,
                listener_id=listener_id,
            )
            return
        self.db.users.update_one(
            {"username": client.friendly_username},
            {
                "$set": {
                    f"disks.{message['disk_id']}": {"content": message["val"]},
                }
            },
        )
        await self.cl.send_code(
            client, "OK", listener_detected=listener_detected, listener_id=listener_id
        )

    async def append_disk(self, client, message, listener_detected, listener_id):
        if not self.CA.IsAuthed(client):
            await self.cl.send_code(
                client,
                "NotLoggedIn",
                listener_detected=listener_detected,
                listener_id=listener_id,
            )
            return
        usr = self.db.users.find_one({"username": client.friendly_username})
        if len(usr.get("disks", [])) < message["disk_id"]:
            await self.cl.send_code(
                client,
                "DiskNotFound",
                listener_detected=listener_detected,
                listener_id=listener_id,
            )
            return
        self.db.users.update_one(
            {"username": client.friendly_username},
            {
                "$set": {
                    f"disks.${message['disk_id']}": usr.get("disks", [])[
                        message["disk_id"]
                    ]
                    + message["val"],
                }
            },
        )
        await self.cl.send_code(
            client, "OK", listener_detected=listener_detected, listener_id=listener_id
        )
