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
        print("Connected, press CTRL+C to disconnect.")

        # Wait for CTRL+C
        try:
            while True: pass
        except KeyboardInterrupt:
            print("Going away in a second")
            await client.asyncio.sleep(1)
        
        client.disconnect()

    # Example use of decorator functions within the server.
    @client.on_command(cmd="gmsg")
    async def on_gmsg(message):
        await client.send_packet({"cmd": "direct", "val": "Hello, server!"})

    # Enable SSL support (if you use self-generated SSL certificates)
    #client.enable_ssl(certfile="cert.pem")

    # Start the client
    client.run(host="ws://127.0.0.1:3000/")
