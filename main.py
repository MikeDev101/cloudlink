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
    cl_protocol = clpv4(server)
    scratch_protocol = scratch(server)

    # Disable CL commands
    for command in ["gmsg", "gvar"]:
        server.disable_command(command, cl_protocol.protocol)

    # Create a demo command
    @server.on_command(cmd="test", schema=cl_protocol.protocol)
    async def on_test(client, message):
        print(message)

    # Configure protocol settings
    # cl_protocol.warn_if_multiple_username_matches = False

    # Configure max clients
    server.max_clients = 2

    # Start the server
    server.run(port=3000)
