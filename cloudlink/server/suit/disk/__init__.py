class CloudDisk:
    def __init__(self, cl):
        self.cl = cl
        self.suporter = self.cl.supporter
        self.db = self.cl.db
        self.CA = self.cl.manager.CA
        self.suporter.codes.extend(
            {
                "StoreageFull": ("E", 117, "Storage is full"),
                "StoreageNotFound": ("E", 118, "Storage not found"),
            }
        )

    async def create_disk(
        self, client, message, listener_detected, listener_id, room_id
    ):
        if not self.CA.isAuthed(client):
            await self.cl.send_status(
                client,
                "NotLoggedIn",
                listener_detected=listener_detected,
                listener_id=listener_id,
            )
            return

        usr = self.db.find_one({"username", client.username})

        if len(usr["disks"]) > 10:
            await self.cl.send_status(
                client,
                "StorageFull",
                listener_detected=listener_detected,
                listener_id=listener_id,
            )
            return

        self.db.update_one(
            {"username": client.username},
            {
                "$push": {
                    "disks": {
                        len(usr["disks"]): {
                            "data": message["val"],
                        }
                    }
                }
            },
        )
        await self.cl.send_status(
            client, "OK", listener_detected=listener_detected, listener_id=listener_id
        )

        rx_client = self.cl.users.get_all_with_username(client.username)
        if not (len(rx_client) == 0):
            await self.cl.send_packet(
                rx_client,
                {
                    "cmd": "update_disks",
                    "val": len(usr["disks"]) + 1,
                    "origin": client.id,
                },
            )

    async def delete_disk(
        self, client, message, listener_detected, listener_id, room_id
    ):
        if not self.CA.isAuthed(client):
            await self.cl.send_status(
                client,
                "NotLoggedIn",
                listener_detected=listener_detected,
                listener_id=listener_id,
            )
            return

        usr = self.db.find_one({"username": client.username})
        if len(usr["disks"]) < message["disk_id"]:
            await self.cl.send_status(
                client,
                "DiskNotFound",
                listener_detected=listener_detected,
                listener_id=listener_id,
            )
            return
            self.db.update_one(
                {"username": client.username},
                {
                    "$pull": {
                        "disks": message["disk_id"],
                    }
                },
            )

        await self.cl.send_status(
            client, "OK", listener_detected=listener_detected, listener_id=listener_id
        )

        rx_client = self.cl.users.get_all_with_username(client.username)
        if not (len(rx_client) == 0):
            await self.cl.send_packet(
                rx_client,
                {
                    "cmd": "update_disks",
                    "val": len(usr["disks"]) - 1,
                    "origin": client.id,
                },
            )

        async def get_disk(
            self, client, message, listener_detected, listener_id, room_id
        ):
            if not self.CA.isAuthed(client):
                await self.cl.send_status(
                    client,
                    "NotLoggedIn",
                    listener_detected=listener_detected,
                    listener_id=listener_id,
                )
                return

            usr = self.db.find_one({"username": client.username})
            if len(usr["disks"]) < message["disk_id"]:
                await self.cl.send_status(
                    client,
                    "DiskNotFound",
                    listener_detected=listener_detected,
                    listener_id=listener_id,
                )
                return

            await self.cl.send_status(
                client,
                "OK",
                extra_data={
                    "disk": {
                        "id": message["disk_id"],
                        "data": usr["disks"][message["disk_id"]],
                    }
                },
                listener_detected=listener_detected,
                listener_id=listener_id,
            )

    async def update_disk(
        self, client, message, listener_detected, listener_id, room_id
    ):
        if not self.CA.isAuthed(client):
            await self.cl.send_status(
                client,
                "NotLoggedIn",
                listener_detected=listener_detected,
                listener_id=listener_id,
            )
            return

        usr = self.db.find_one({"username": client.username})
        if len(usr["disks"]) < message["disk_id"]:
            await self.cl.send_status(
                client,
                "DiskNotFound",
                listener_detected=listener_detected,
                listener_id=listener_id,
            )
            return
        self.db.update_one(
            {"username": client.username},
            {
                "$set": {
                    f"disks.${message['disk_id']}": message["val"],
                }
            },
        )
        await self.cl.send_status(
            client, "OK", listener_detected=listener_detected, listener_id=listener_id
        )

    async def append_disk(
        self, client, message, listener_detected, listener_id, room_id
    ):
        if not self.CA.isAuthed(client):
            await self.cl.send_status(
                client,
                "NotLoggedIn",
                listener_detected=listener_detected,
                listener_id=listener_id,
            )
            return
        usr = self.db.find_one({"username": client.username})
        if len(usr["disks"]) < message["disk_id"]:
            await self.cl.send_status(
                client,
                "DiskNotFound",
                listener_detected=listener_detected,
                listener_id=listener_id,
            )
            return
        self.db.update_one(
            {"username": client.username},
            {
                "$set": {
                    f"disks.${message['disk_id']}": usr["disks"][message["disk_id"]]
                    + message["val"],
                }
            },
        )
        await self.cl.send_status(
            client, "OK", listener_detected=listener_detected, listener_id=listener_id
        )
