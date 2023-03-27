from cloudlink import client
from cloudlink.client.protocols import clpv4

if __name__ == "__main__":
    # Initialize the client
    client = client()
    
    # Configure logging settings
    client.logging.basicConfig(
        level=client.logging.DEBUG
    )

    # Load protocols
    clpv4 = clpv4(client)

    # Initialize SSL support
    client.enable_ssl(certfile="cert.pem")
    
    # Start the server
    client.run(host="wss://cloudlink.ddns.net:3000/")
