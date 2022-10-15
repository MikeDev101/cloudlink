from cloudlink import cloudlink
from asyncio import sleep


class callback_examples:
    def __init__(self):
        pass

    async def on_connect(self, client):
        #print(f"Client {client.obj_id} connected")
        #logging in
        await client.send_raw_packet({
            "cmd": "signup",
            "username": "a",
            "password": "b"
        })

        await sleep(1)
        await client.send_raw_packet({
            "cmd": "login",
            "username": "a",
            "password": "b"
        })

        #coins
        await client.send_raw_packet({"cmd": "add_coins", "ammount": 3})

        await sleep(1)
        await client.send_raw_packet({"cmd": "spend_coins", "ammount": 2})

        #disk
        await client.send_raw_packet({"cmd": "create_disk", "val": 'e'})
        await sleep(1)
        await client.send_raw_packet({"cmd": "get_disk", "disk_id": 0})
        await sleep(1)
        await client.send_raw_packet({
            "cmd": "update_disk",
            "disk_id": 0,
            "val": "updated"
        })
        await client.send_raw_packet({"cmd": "delete_disk", "disk_id": 0})

    async def on_close(self, client):
        #print(f"Client {client.obj_id} disconnected")
        pass

    async def username_set(self, client):
        #print(f"Client {client.obj_id}'s username was set!")
        pass

    async def on_gmsg(self, client, message, listener_detected, listener_id):
        #print(f"Client {client.obj_id} got gmsg {message['val']}")
        pass


if __name__ == "__main__":
    cl = cloudlink()
    example = callback_examples()

    client = cl.client(logs=False)
    client.bind_event(
        client.events.on_connect, example.on_connect
    )  # When a client connects, all functions bound to this event will fire.
    client.bind_event(
        client.events.on_close, example.on_close
    )  # When a client disconnects, all functions bound to this event will fire.
    client.bind_event(
        client.events.on_username_set, example.username_set
    )  # When a client disconnects, all functions bound to this event will fire.

    client.run(ip="wss://Cloudlink.showierdata9971.repl.co/")
