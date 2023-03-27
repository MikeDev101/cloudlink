from cloudlink import server
from cloudlink.server.plugins import cl_admin
from cloudlink.server.protocols import clpv4, scratch

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

    # Initialize SSL support
    # server.enable_ssl(certfile="cert.pem", keyfile="privkey.pem")
    
    # Start the server
    server.run(ip="127.0.0.1", port=3000)
