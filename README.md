![Cloudlink_logo-2](https://user-images.githubusercontent.com/12957745/153096387-f500ec71-ea94-4ed4-a9f6-bbff8facc262.png)

# CloudLink

CloudLink is a high-speed, reliable, and custom websocket extension for Scratch 3.0, with server code that runs on Python.
It permits cross-project (as well as cross-program) cloud variables.
It also enables full-duplex networking and limitless possibilities for Scratch 3.0 projects.
## Links

### [HackMD Documentation](https://hackmd.io/G9q1kPqvQT6NrPobjjxSgg)
### [CloudLink JS (cljs)](https://github.com/wgyt/cljs)

## Example code
Example code can be downloaded in the GitHub repository.

#### Server: https://github.com/MikeDev101/cloudlink/blob/master/server_example.py
#### Client: https://github.com/MikeDev101/cloudlink/blob/master/client_example.py

Please report any bugs you find to the official [GitHub repository](https://github.com/MikeDev101/cloudlink/issues).


# Scratch Extension
You can view the client-side extension using one of the following modded Scratch editors:
* [TurboWarp](https://turbowarp.org/editor?extension=https://mikedev101.github.io/cloudlink/B3-0.js)
* [SheepTester's E羊icques](https://sheeptester.github.io/scratch-gui/?url=https://mikedev101.github.io/cloudlink/B3-0.js)
* [Ogadaki's Adacraft (Manual load required)](https://adacraft.org/studio/)

# Installing CloudLink
## Method 1: using pip
```pip install cloudlink```

## Method 2: Directly downloading cloudlink.py
Simply download the [source code](https://github.com/MikeDev101/cloudlink/archive/refs/heads/master.zip), extract cloudlink.py, and import it as shown above. However, the following dependencies are required in order to take advantage of full functionality:
* websocket-server ```pip install websocket-server```
* websocket-client ```pip install websocket-client```
