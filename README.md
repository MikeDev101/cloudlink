# CloudLink

CloudLink is an API for Scratch 3. It's basically cloud variables, but better.

## How it works

CloudLink connects to a hosted server, either on the localhost or through a port forwarded static ip or a reverse proxy such as ngrok. The client is a [E羊icques](https://sheeptester.github.io/scratch-gui/) extension, and all that is needed is to add the extension, and an internet connection (if not using the localhost).

## Usage

### E羊icques extension (index.js)
All blocks are self-explained, and easy to use. Simply fill-in the blanks (urls, and your data) to use. The blocks also report info such as if the connection is already made, or not. Simply load the scratch 3 mod and add the index.js file.

### Server.py
Simply run the server, and it will automatically start running! Simple as that. By default, it runs through ws://localhost:3000/, but you can reconfigure it within the python file. To expose the server to the world, simply port foward the ip and port, or use a reverse proxy (I recommend ngrok!).

## Click [here](https://sheeptester.github.io/scratch-gui/?url=https://mikedev101.github.io/cloudlink/cloudlink.js) to try the extension.
