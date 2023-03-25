from cloudlink import server
from cloudlink.protocols import clpv4, scratch

if __name__ == "__main__":
    # Initialize the server
    server = server()
    
    # Configure logging settings
    server.logging.basicConfig(
        format="[%(asctime)s] %(levelname)s: %(message)s",
        level=server.logging.INFO
    )

    # Load protocols
    clpv4 = clpv4(server)
    scratch = scratch(server)
    
    # Init SSL
    server.enable_ssl(certfile = "cert.pem", keyfile = "privkey.pem")
    
    # Start the server
    server.run(ip="0.0.0.0", port=3000)
