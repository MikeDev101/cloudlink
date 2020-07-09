# CloudLink

CloudLink is an API for Scratch 3. It's basically cloud variables, but better.

## How it works

CloudLink connects to a hosted server, either on the localhost or through a port forwarded static ip or a reverse proxy such as ngrok. The client is a [E羊icques](https://sheeptester.github.io/scratch-gui/) extension, and all that is needed is to add the extension, and an internet connection (if not using the localhost).

# What does it look like, and how do I use it?

Take a look at this!

![Documentation I totally made in MS paint](https://u.cubeupload.com/MikeDEV/new.jpg)

### Server: server.py
Simply run the server, and it will automatically start running! Simple as that. By default, it runs through ws://localhost:3000/, but you can reconfigure it within the python file. To expose the server to the world, simply port foward the ip and port, or use a reverse proxy (I recommend ngrok!).

## Click [here](https://sheeptester.github.io/scratch-gui/?url=https://mikedev101.github.io/cloudlink/cloudlink.js) to try the extension.
