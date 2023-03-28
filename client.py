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

    @client.on_connect
    async def on_connect():
        client.send_packet({"cmd": "handshake"})
        print("Connected")
    
    # Start the server
    client.run(host="ws://127.0.0.1:3000/")
