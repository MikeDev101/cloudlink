# Database support
With CloudLink 4 Server, CloudLink Suite is a built-in feature that can be enabled on a per-server basis.
The CloudLink Suite supports the following database systems:

* MongoDB through a local or cloud-based MongoDB Server
* TinyDB as a local .json file

Or you can use the Legacy "NoDB" mode, which uses the local filesystem for storing user data.

(NODB MODE IS NOT RECOMMENDED)

# Adding custom command handlers
To add a custom command handler, simply create a new class with your custom handler functions, and to add the commands to CloudLink simply use
the load_custom_commands() function.

```
from cloudlink import CloudLink
...
class yourclass:
  def __init__(self):
    # You can add whatever you want to the class initializer.
  def your_function_here(self, packet_data):
    # Specify what your custom command does here
...
cl = CloudLink() # Instanciate CloudLink
custom = yourclass() # Instanciate your custom command set
cl.load_custom_commands(custom) # Load and auto-bind your commands into CloudLink
cl.server(ip="0.0.0.0", port=3000) # Start the server
```
