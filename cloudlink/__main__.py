from cloudlink import Cloudlink

if __name__ == "__main__":
    print("Welcome to Cloudlink!\nSince you are calling Cloudlink directly, there is now a websocket server running on ws://127.0.0.1:3000/.\nPlease visit https://github.com/MikeDev101/cloudlink to report bugs and/or get help!")

    # Initialize Cloudlink. You will only need to initialize one instance of the main cloudlink module.
    cl = Cloudlink()
    
    # Create a new server object. This supports initializing many server at once.
    server = cl.server(logs=True)

    # Set the server's Message-Of-The-Day.
    server.setMOTD(True, "CloudLink 4 Test")

    # Run the server
    server.run(host="127.0.0.1", port=3000)