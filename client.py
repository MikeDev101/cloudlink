from cloudlink import client

if __name__ == "__main__":
    # Initialize the client
    client = client()
    
    # Configure logging settings
    client.logging.basicConfig(
        level=client.logging.DEBUG
    )

    # Example of events
    @client.on_connect
    async def on_connect():
        print("Connected")
    
    # Start the server
    client.run(host="ws://127.0.0.1:3000/")
