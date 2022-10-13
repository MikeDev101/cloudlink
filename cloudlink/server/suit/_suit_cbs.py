class suit_cbs:
    """
    demoCallbacksServer

    This is an example of Cloudlink's callback system.
    """

    def __init__(self, cloudlink):
        # To use callbacks, you will need to initialize your callbacks class with Cloudlink. This is required.
        self.cloudlink = cloudlink

    async def on_packet(self, *args):
        await self.cloudlink.suit.call_callbacks("on_packet", *args)

    async def on_connect(self, client):
        await self.cloudlink.suit.call_callbacks("on_connect", client)

    async def on_close(self, client):
        await self.cloudlink.suit.call_callbacks("on_close", client)

    # Below are templates for binding command-specific callbacks. These commands are already handled in the server, but you can extend functionality using this feature.

    async def on_direct(
        self, message: any, origin: any, listener_detected: bool, listener_id: str
    ):  # Called when a packet is handled with the direct command.
        await self.cloudlink.suit.call_callbacks(
            "on_direct", message, origin, listener_detected, listener_id
        )

    async def on_setid(
        self, motd: str
    ):  # Called when a packet is handled with the setid command.
        await self.cloudlink.suit.call_callbacks("on_setid", motd)

    async def on_ulist(
        self, ulist: list
    ):  # Called when a packet is handled with the ulist command.
        await self.cloudlink.suit.call_callbacks("on_ulist", ulist)

    async def on_statuscode(
        self, code: str, message: any
    ):  # Called when a packet is handled with the statuscode command.
        await self.cloudlink.suit.call_callbacks("on_statuscode", code, message)

    async def on_gmsg(
        self, message: any
    ):  # Called when a packet is handled with the gmsg command.
        await self.cloudlink.suit.call_callbacks("on_gmsg", message)

    async def on_gvar(
        self, var_name: str, var_value: any
    ):  # Called when a packet is handled with the gvar command.
        await self.cloudlink.suit.call_callbacks("on_gvar", var_name, var_value)

    async def on_pvar(
        self, var_name: str, var_value: any, origin: any
    ):  # Called when a packet is handled with the pvar command.
        await self.cloudlink.suit.call_callbacks("on_pvar", var_name, var_value, origin)

    async def on_pmsg(
        self, value: str, origin: any
    ):  # Called when a packet is handled with the pmsg command.
        await self.cloudlink.suit.call_callbacks("on_pmsg", value, origin)

    async def on_ping(self, value: str, origin: any):  # Called when a ping is handled.
        await self.cloudlink.suit.call_callbacks("on_ping", value, origin)
