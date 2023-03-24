from cloudlink import cloudlink
from cloudlink.protocols import clpv4, scratch

if __name__ == "__main__":
    # Initialize the server
    server = cloudlink.server()

    # Configure logging settings
    server.logging.basicConfig(
        format="[%(asctime)s] %(levelname)s: %(message)s",
        level=server.logging.DEBUG
    )

    # Load protocols
    clpv4 = clpv4(server)
    # scratch = scratch(server)

    # Disable CL commands
    for command in ["gmsg", "gvar"]:
        server.disable_command(cmd=command, schema=clpv4.schema)

    # Create a demo command
    @server.on_command(cmd="test", schema=clpv4.schema)
    async def on_test(client, message):
        print(message)

    # Start the server
    server.run(port=3000)
