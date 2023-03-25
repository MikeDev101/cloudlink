from cloudlink import server
from cloudlink.protocols import clpv4, scratch
import ssl

if __name__ == "__main__":
    # Initialize the server
    server = server()
    
    # Initialize SSL
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    certfile = "cert.pem"
    keyfile = "privkey.pem"
    ssl_context.load_cert_chain(certfile=certfile, keyfile=keyfile)
    
    # Configure logging settings
    server.logging.basicConfig(
        format="[%(asctime)s] %(levelname)s: %(message)s",
        level=server.logging.INFO
    )

    # Load protocols
    clpv4 = clpv4(server)
    scratch = scratch(server)

    # Disable CL commands
    for command in ["gmsg", "gvar"]:
        server.disable_command(cmd=command, schema=clpv4.schema)

    # Create a demo command
    @server.on_command(cmd="test", schema=clpv4.schema)
    async def on_test(client, message):
        print(message)
    
    # Pass the SSL context to the server
    server.enable_ssl(ssl_context)
    
    # Start the server
    server.run(ip="0.0.0.0", port=3000)
