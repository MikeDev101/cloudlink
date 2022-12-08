from cloudlink import cloudlink
from cloudlink.home_server import home, DataBase


if __name__ == "__main__":
    # Initialize Cloudlink. You will only need to initialize one instance of the main cloudlink module.
    cl = cloudlink()

    # Create a new server object. This supports initializing many servers at once.
    server = cl.server(logs=True)
    cl_home = home(server, DataBase())

    # Create examples for various ways to extend the functionality of Cloudlink Server.


    # Set the message-of-the-day.
    server.set_motd("CL4 Optimized Home Server!", True)

    # Run the server.
    server.run(ip="localhost", port=3000)
