from cloudlink import CloudLink
from cloudlink.Suit.CloudAccount import CloudAccount
"""

CloudLink Server Example

This demonstrates the new features of CloudLink server as of 0.1.7.2.
For more information, please visit https://hackmd.io/G9q1kPqvQT6NrPobjjxSgg

"""

def on_packet(message):
    # We can get the IP of the client
    if type(message["id"]) == dict:
        print("Username is not set for this ID, ID is {0}".format(message["id"]["id"]))
        print("IP of unnamed user is {0}".format(cl.getIPofObject(message["id"])))
    elif type(message["id"]) == str:
        print("Username set as {0}".format(message["id"]))
        print("IP of user is {0}".format(cl.getIPofUsername(message["id"])))
    
    # Check for custom commands, of which we can write custom handlers for
    if "cmd" in message:
        print("Detected custom cmd")
        print("cmd is {0}".format(message["cmd"]))
    print("val is", message["val"])
    
    # Send back a status code to the user
    cl.sendPacket({"cmd": "statuscode", "val": cl.codes["OK"], "id": message["id"]})
    #cl.sendPacket({"cmd": "direct", "val": message["val"], "id": message["id"]})
    
def on_connect(client):
    print("New client connected:", client["id"])

def on_error(error):
    print("Got an error: {0}".format(error))

def on_close(client):
    print("Client disconnected:", client["id"])

if __name__ == "__main__":
    cl = CloudLink(debug=True)
    CA = CloudAccount(cl)
    # Instanciate CloudLink
    
    CA.callback("on_packet", on_packet)
    CA.callback("on_error", on_error)
    CA.callback("on_connect", on_connect)
    CA.callback("on_close", on_close)
    # Specify callbacks to functions above
    
    #cl.trustedAccess(True, ["test"])
    # Enable trusted access
    
    cl.setMOTD("CloudLink test", enable=True)
    # Turn on Message-Of-The-Day

    cl.server()
    # Run the server
