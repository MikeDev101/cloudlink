# CloudLink Python
This is the original, Python-based codebase for CloudLink server.

## 💡 Features 💡

### 🪶 Fast and lightweight
CloudLink can run on minimal resources. At least 25MB of RAM and any reasonably capable CPU can run a CloudLink server.

### 🌐 Essential networking tools
* Unicast and multicast packets across clients
* Expandable functionality with a built-in method loader

### 📦 Minimal dependencies
All dependencies below can be installed using `pip install -r requirements.txt`.
* 🐍 Python >=3.11
* 🧵 asyncio (Built-in)
* 📃 ["ujson" ultrajson](https://github.com/ultrajson/ultrajson)
* 🔍 [pyeve/cerberus](https://github.com/pyeve/cerberus)
* ❄️ ["snowflake-id" vd2org/snowflake](https://github.com/vd2org/snowflake)
* 🌐 [aaugustin/websockets](https://github.com/aaugustin/websockets)

### 🔋Batteries included
The CloudLink Python server comes with full support for the CL4 protocol and the Scratch cloud variable protocol.
Just download, setup, and start!

### 🧱 Plug-and-play modularity
You can easily extend the functionality of the server using classes and decorators. 
Here's an example of a simple plugin that displays "Foobar!" in the console
when a client sends the message `{ "cmd": "foo" }` to the server.

```python
# Import the server
from cloudlink import server

# Import default protocol
from cloudlink.server.protocols import clpv4

# Instantiate the server object
server = server()

# Set logging level
server.logging.basicConfig(
    level=server.logging.DEBUG
)

# Load default CL protocol
clpv4 = clpv4(server)

# Define the functions your plugin executes
class myplugin:
    def __init__(self, server, protocol):
        
        # Example command - client sends { "cmd": "foo" } to the server, this function will execute
        @server.on_command(cmd="foo", schema=protocol.schema)
        async def foobar(client, message):
            print("Foobar!")

# Load the plugin!
myplugin(server, clpv4)

# Start the server!
server.run()
```
