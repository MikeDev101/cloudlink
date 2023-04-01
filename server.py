
from cloudlink.server.plugins import cl_admin
from cloudlink.server.protocols import clpv4, scratch
from cloudlink.server.protocols.clpv4.schema import cl4_protocol

cl4_protocol.mycommand = {
    "cmd": {
        "type": "string",
        "required": True
    },
    "val": {
        "type": [
            "string",
            "integer",
            "float",
            "number",
            "boolean",
            "dict",
            "list",
            "set",
        ],
        "required": False,
    },
}

from cloudlink.server import plugin, command

from cloudlink import server

class my_plugin(plugin):
    def __init__(self, server):
        super().__init__()
        self.server = server

    @command("statuscode", cl4_protocol)
    async def mycommand(self, client, data):
        await self.server.clpv4.send_statuscode(client, self.server.clpv4.statuscodes.ok)
    

if __name__ == "__main__":
    # Initialize the server
    server = server()
    
    # Configure logging settings
    server.logging.basicConfig(
        level=server.logging.DEBUG
    )

    # Load protocols
    clpv4 = clpv4(server)
    scratch = scratch(server)

    # Load plugins
    cl_admin = cl_admin(server, clpv4)

    # Load custom plugin
    my_plugin = my_plugin(server)

    server.load_plugin(my_plugin)

    # Initialize SSL support
    # server.enable_ssl(certfile="cert.pem", keyfile="privkey.pem")
    
    # Start the server
    server.run(ip="127.0.0.1", port=3000)
