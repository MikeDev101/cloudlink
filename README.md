# CloudLink

CloudLink is a high-speed, reliable, and custom websocket extension for Scratch 3.0, with server code that runs on Python.
It permits cross-project (as well as cross-program) cloud variables.
It also enables full-duplex networking and limitless possibilities for Scratch 3.0 projects.

Example usage:
```
from cloudlink import CloudLink

cl = CloudLink()
cl.host(3000) # Hosts CloudLink in Server Mode on ws://localhost:3000/
```

Please report any bugs you find to the official [GitHub repository](https://github.com/MikeDev101/cloudlink/issues) or on
my [Scratch profile.](https://scratch.mit.edu/users/MikeDEV/)


# Scratch Extension
You can view the client-side extension using one of the following modded Scratch editors:
* [TurboWarp](https://turbowarp.org/editor?extension=https://mikedev101.github.io/cloudlink/B3-0.js)
* [SheepTester's E羊icques](https://sheeptester.github.io/scratch-gui/?url=)
* _Adacraft support WIP..._

# Installing CloudLink
## Method 1: using pip3 (This is WIP and may not work)
```pip3 install cloudlink```

## Method 2: Directly downloading cloudlink.py
Simply download cloudlink.py and import it as shown above. However, the following dependencies are required in order to take advantage of full functionality:
* websocket-server ```pip3 install websocket-server```
* websocket-client ```pip3 install websocket-client```
