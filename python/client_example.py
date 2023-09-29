from cloudlink import client

if __name__ == "__main__":
    # Initialize the client
    client = client()
    
    # Configure logging settings
    client.logging.basicConfig(
        level=client.logging.DEBUG
    )

    # Use this decorator to handle established connections.
    @client.on_connect
    async def on_connect():
        print("Connected!")

        # Ask for a username
        await client.protocol.set_username(input("Please give me a username... "))

        # Whenever a client is connected, you can call this function to gracefully disconnect.
        # client.disconnect()
    
    # Use this decorator to handle disconnects.
    @client.on_disconnect
    async def on_disconnect():
        print("Disconnected!")
    
    # Use this decorator to handle username being set events.
    @client.on_username_set
    async def on_username_set(id, name, uuid):
        print(f"My username has been set! ID: {id}, Name: {name}, UUID: {uuid}")
    
    # Example message-specific event handler. You can use different kinds of message types,
    # such as pmsg, gvar, pvar, and more.
    @client.on_gmsg
    async def on_gmsg(message):
        print(f"I got a global message! It says: \"{message['val']}\".")

    # Example use of on_command functions within the client.
    @client.on_command(cmd="gmsg")
    async def on_gmsg(message):
        client.send_packet({"cmd": "direct", "val": "Hello, server!"})

    # Enable SSL support (if you use self-generated SSL certificates)
    #client.enable_ssl(certfile="cert.pem")

    # Start the client
    client.run(host="ws://127.0.0.1:3000/")
