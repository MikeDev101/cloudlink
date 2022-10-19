import secrets
import uuid
import time

from cloudlink import cloudlink
from cloudlink.server.server import clients


class Servers(clients):
    def __init__(self, db, *args, **kwargs):
        super(clients, self).__init__(*args, **kwargs)
        self.servers = {}
        self.db = db

    def add_server(self, server_client, server_secret):

        server = self.db.servers.find_one({"secret": server_secret})
        if server is None:
            return False

        server_client.secret = server_secret

        trades = server["known_trades"]

        # Save server secrets that can trade with it
        self.servers[server_secret] = {
            "name": server["name"],
            "client": server_client,
            "secret": server_secret,
            "known_trades": trades,
        }
        return True


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
        self.servers = Servers(self.db)

        self.supporter.codes.update(
            {
                "NotEnoughCoins": (
                    "I",
                    115,
                    "Your dont have enough coins",
                ),
                "ProjectNotFound": ("E", 116, "Project not registered"),
            }
        )

    # when someone transfers to CC the projects coins are worth less in CC
    async def transfer_to_project(
        self, client, message, listener_detected, listener_id
    ):
        if not self.CA.IsAuthed(client):
            await self.cl.send_code(
                client,
                "NotLoggedIn",
                listener_detected=listener_detected,
                listener_id=listener_id,
            )
            return

        project = self.db.projects.find_one({"name": message["project"]})
        if not project:
            await self.cl.send_code(
                client,
                "ProjectNotFound",
                listener_detected=listener_detected,
                listener_id=listener_id,
            )
            return

            if (
                project["secret"]
                not in self.servers.servers[hash(message["secret"])]["known_trades"]
            ):
                await self.cl.send_code(
                    client,
                    "Unauthorized",
                    listener_detected=listener_detected,
                    listener_id=listener_id,
                )
                return

            if (
                message["secret"]
                not in self.servers.servers[project["secret"]]["known_trades"]
            ):
                await self.cl.send_code(
                    client,
                    "Unauthorized",
                    listener_detected=listener_detected,
                    listener_id=listener_id,
                )

            await self.cl.send_packet_multicast(
                self.servers.servers[project["secret"]]["client"],
                cmd="update_coins",
                val={
                    "user": message["user"],
                    "project": message["project"],
                    "amount": message["amount"],
                },
            )

            await self.cl.send_code(
                client,
                "OK",
                listener_detected=listener_detected,
                listener_id=listener_id,
            )

    async def add_tradable_project(
        self, client, message, listener_detected, listener_id
    ):
        if not self.CA.IsAuthed(client):
            await self.cl.send_code(
                client,
                "NotLoggedIn",
                listener_detected=listener_detected,
                listener_id=listener_id,
            )
            return

        self.db.projects.update(
            {
                "secret": message["secret"],
            },
            {
                "$push": {
                    "known_trades": message["secret"],
                }
            },
        )

    async def login_project(self, client, message, listener_detected, listener_id):
        if not self.CA.IsAuthed(client):
            await self.cl.send_code(
                client,
                "NotLoggedIn",
                listener_detected=listener_detected,
                listener_id=listener_id,
            )
            return

        usr = self.db.users.find_one({"username": client.frendly_username})
        project = self.db.projects.find_one({"owner_id": usr["_id"]})

        if not project:
            await self.cl.send_code(
                client,
                "ProjectNotFound",
                listener_detected=listener_detected,
                listener_id=listener_id,
            )

        self.servers.add_server(
            client,
            project["secret"],
        )

        await self.cl.send_code(
            client,
            "OK",
            listener_detected=listener_detected,
            listener_id=listener_id,
            extra_data={"secret": project["secret"]},
        )

    async def register_project(self, client, message, listener_detected, listener_id):
        if not self.CA.IsAuthed(client):
            await self.cl.send_code(
                client,
                "NotLoggedIn",
                listener_detected=listener_detected,
                listener_id=listener_id,
            )
            return

        usr = self.db.users.find_one({"name": client.frendly_username})

        secret = secrets.token_urlsafe()
        self.db.projects.insert_one(
            {
                "secret": secret,
                "name": message["name"],
                "known_trades": [],
                "owner_id": usr["_id"],
            }
        )
        self.servers.add_server(client, secret)
