# CloudLink

CloudLink is an API for Scratch 3. It's basically cloud variables, but better.

## How it works

CloudLink connects to a hosted server, either on the localhost or through a port forwarded static ip or a reverse proxy such as ngrok. The client is a [E羊icques](https://sheeptester.github.io/scratch-gui/) extension, and all that is needed is to add the extension, and an internet connection (if not using the localhost).

## Usage

### Client: cloudlink.js
All blocks are self-explained, and easy to use. Simply fill-in the blanks (urls, and your data) to use. The blocks also report info such as if the connection is already made, or not. Simply load the scratch 3 mod and add the cloudlink.js file.

### ![socketdata_global](https://cdn.glitch.com/2d2fd699-1471-4a63-af1a-c7b7677c8b13%2Fsocketdataglobal.png?v=1587745339046)
This reporter block returns all the data received over the global data stream. Everyone has access to this data, and anyone can see what is received.

### ![socketdata_private](https://cdn.glitch.com/2d2fd699-1471-4a63-af1a-c7b7677c8b13%2Fsocketdataprivate.png?v=1587745342598)
This reporter block returns all the data received over your private data stream. Only you can see this data, but anyone can send you things.

### ![userlist](https://cdn.glitch.com/2d2fd699-1471-4a63-af1a-c7b7677c8b13%2Fuserlist.png?v=1587745333267)
This reporter block returns a list of all the users connected to the websocket server.

### ![fetchuserlist](https://cdn.glitch.com/2d2fd699-1471-4a63-af1a-c7b7677c8b13%2Ffetchuserlist.png?v=1587745359528)
This command block refreshes the user list reporter's data.

### ![connect](https://cdn.glitch.com/2d2fd699-1471-4a63-af1a-c7b7677c8b13%2Fconnect2server.png?v=1587745366554)
This command block establishes a connection to the websocket server. The server must have server.py running on port 3000 (the default port), or it won't work.

### ![disconnect](https://cdn.glitch.com/2d2fd699-1471-4a63-af1a-c7b7677c8b13%2Fdisconnectfromserver.png?v=1587745369394)
This command block disconnects from the websocket server, if it is connected.

## ![broadcastid](https://cdn.glitch.com/2d2fd699-1471-4a63-af1a-c7b7677c8b13%2Fbroadcastid.png?v=1587745376197)
This command block broadcasts your name to the user list, and this enables usage of the private data stream. If this script isn't called when you connect, you will only have access to the global data stream.

## ![sendglobal](https://cdn.glitch.com/2d2fd699-1471-4a63-af1a-c7b7677c8b13%2Fsendglobal.png?v=1587745383581)
This command block sends data through the global data stream.

## ![getdataglobal](https://cdn.glitch.com/2d2fd699-1471-4a63-af1a-c7b7677c8b13%2Ffetchglobal.png?v=1587745386745)
This command block updates the global socket data reporter.

## ![sendprivate](https://cdn.glitch.com/2d2fd699-1471-4a63-af1a-c7b7677c8b13%2Fsendprivate.png?v=1587745392186)
This command block sends data to someone through the private data stream.

## ![getdataprivate](https://cdn.glitch.com/2d2fd699-1471-4a63-af1a-c7b7677c8b13%2Ffetchprivate.png?v=1587745395309)
This command block updates yor private socket data reporter.

### Server: server.py
Simply run the server, and it will automatically start running! Simple as that. By default, it runs through ws://localhost:3000/, but you can reconfigure it within the python file. To expose the server to the world, simply port foward the ip and port, or use a reverse proxy (I recommend ngrok!).

## Click [here](https://sheeptester.github.io/scratch-gui/?url=https://mikedev101.github.io/cloudlink/cloudlink.js) to try the extension.
