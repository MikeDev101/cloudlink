// MikeDEV's CloudLink API
// Version 0.1.5 - Built upon KingdomPi's Scratch-websockets repo.
// See https://github.com/KingdomPy/scratch_websockets/blob/master/index.js for the original script!
//

const vers = '0.1.5';

const blockIconURI = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFAAAABQCAYAAACOEfKtAAAE9ElEQVR4Xu2aS4gcVRSGv9MOjSJowI0RRONODDKj0tUDMzgjggohKgRFETIRcaUwoqAIkkR04QMi6saFzEhIBAMad7rK+JyujpCIoBsfCcTHMiIIMdpHqh+T6Zl6dZ3qeYRzl133P3Xq6//ec++tEryZCIhJ7WIcoNEEDtABGgkY5e5AB2gkYJS7Ax2gkYBR7g50gEYCRrk70AEaCRjl7kAHaCRglLsDHaCRgFHuDnSARgJGuTvQARoJGOXuQAdoJGCUuwM3BMATuoVzHECY6eZzEmEPNTlpzK88eaj3Abu7Ad8jkKNlBLc7MIL3D8eA0RUJnUWY3hAQQ51fBq+X5j4C2W+FaAOYDK+Tl7BATaatSZr0DZ1FOBAbQ5mnLnss8YsDzILXyyqQ4vewPFlPG+op4LrEUEaIxR4uLzz4k0C2lMGhcIxQNYd2P4Hsy9FvVZfBAeaHF92scGJFHiZWE2pULO7NjNcpetFcOVAbDOBg8D4jkKmBshlG507O0TC+MjN8AYj5AQ4G71uqTDEmZzOTXosOTR1FWRgGxHwANzO83h80JIj5AOadR2BjOW+lu4cAMRtg/CI0buBtbHhDcmI6wLLhhfowMAH8wggfcav8mDgFHtc7abETuLo9f40wz23yd2z/ht4M7KLCTcAiIxzmFvktMXaJTkwGWCa8pj6IMgdc1vdQwhvU5Km+3xp6BcIHwF19vyv/Ao9Sl4N9v4f6FvBEDKxnCeTVYUOMB1gmvON6Ay1+Sim2zxHIK0vXm/oOyuOJ/YWt1OSP9vVQnwTeTOyr3EFdon16fCvBiasBlgkvSruhryM8nbpa6W33mhoN199T+yp7qcuLXYBZu4wjBPJAajwjxH6A+eGdpspornVeqD8D2zKgTFKXLwn1IeBwxtIwJJA6i3ojFb7P6HuOQC7NXGo2daY7xWR27R7TLe1Y+gEaAqUMk19RrsnI7G4C+ZROkTmU2ldoUpOAr3Q7I3yXEfc8gVQzqXTWuSeA6zP7Rku1QJaO7lYP4bIhNnUOXTpojc/vEi5vV9hvdCv/kVw9O+oL++vsg4KjBHJ/JpRQo13K7Zn9Yta58UWkTIgNnUD4IiW5twkkKgadFuq77Wqb1JRrqcuZ9uWmPoPyWmJf4R5q8kkqmPzTVuw6N3kZUybEUF8Gno95kM85zw4m5K9lAK8CjgBxB7GPEUgE+EJr6EGER1bFVl6iLi8ME14UO30hPQjEFtOMSzQU4tvXOkaF3VSYRIkKy4cE8n5i/1B3oOyk0l5IH6PKXGLRCnUSYRfK9vZCusUhxuWHYcPLBtgZJnkr1MZ5B5I1mRmH7fLw2Xvhiw1iifDyObCH+2JwYsnwBgO42Z04BHiDA9ysEIcErxjAwSCeIpD0bVzWhG+9Hmr0tm1vjjCFzjPzFZG4u+edE4Wxdf06IXu3Ej1dIXjFHThIYWmxjXGJ3oqtfeuctER73LRWGJ4dYPZwXv9Xm6FGbwaTXmma4JUDMBniaVpMrZv7ep5b1Ckq7Y+fVjYzvPIARpE6ic52v9JaoMpsrvPCtRjYnU/bojO8nhM/pspMGfkVLyJr8eCb4B4O0PgnOUAHaCRglLsDHaCRgFHuDnSARgJGuTvQARoJGOXuQAdoJGCUuwMdoJGAUe4OdIBGAka5O9ABGgkY5e5AB2gkYJS7Ax2gkYBR7g50gEYCRvn/QEDeYP09rHoAAAAASUVORK5CYII=';
const menuIconURI = blockIconURI; 

class cloudlink{
    constructor (runtime, extensionId) {
        this.isRunning = false;
	this.runtime = runtime;
	this.ID = "";
        this.socketDataGlobalStream = "";
	
	this.socketDataPrivateStream = "";
	this.socketDataPrivateCached = "";
    }

    static get STATE_KEY () {
        return 'Scratch.websockets';
    }

    getInfo () {
        return {
            id: 'cloudlink',
            name: 'CloudLink',
            blockIconURI: blockIconURI,
            color1: '#054c63',
            color2: '#054c63',
            color3: '#043444',
            blocks: [
                {
                    opcode: 'getSocketDataGlobalStream',
                    blockType: Scratch.BlockType.REPORTER,
                    text: 'Socket data (Global stream)',
                },
		{
                    opcode: 'getSocketDataPrivateStream',
                    blockType: Scratch.BlockType.REPORTER,
                    text: 'Socket data (Private stream)',
                },
                {
                    opcode: 'getSocketState',
                    blockType: Scratch.BlockType.BOOLEAN,
                    text: 'Is the socket connected?',
                },
                {
                    opcode: 'openSocket',
                    blockType: Scratch.BlockType.COMMAND,
                    text: 'Connect to socket [WS]',
		    arguments: {
			WS: {
			type: Scratch.ArgumentType.STRING,
			defaultValue: 'ws://localhost:3000/',
			}
		    }
                },
                {
                    opcode: 'closeSocket',
                    blockType: Scratch.BlockType.COMMAND,
                    text: 'Disconnect from socket',
                },
                {
                    opcode: 'sendDataGlobalStream',
                    blockType: Scratch.BlockType.COMMAND,
                    text: 'Send [DATA] through global stream',
                    arguments: {
                        DATA: {
                            type: Scratch.ArgumentType.STRING,
                            defaultValue: 'thing',
                        }
                    }
                },
                {
                    opcode: 'fetchDataGlobalStream',
                    blockType: Scratch.BlockType.COMMAND,
                    text: 'Fetch data through global stream',
                },
		{
                    opcode: 'sendDataPrivateStream',
                    blockType: Scratch.BlockType.COMMAND,
                    text: 'Send [DATA] through private stream to [ID]',
                    arguments: {
                        DATA: {
                            type: Scratch.ArgumentType.STRING,
                            defaultValue: 'thing',
                        },
			ID: {
                            type: Scratch.ArgumentType.STRING,
                            defaultValue: 'user',
                        }
                    }
                },
		{
                    opcode: 'fetchDataPrivateStream',
                    blockType: Scratch.BlockType.COMMAND,
                    text: 'Fetch data through private stream from [ID]',
		    arguments: {
			ID: {
                            type: Scratch.ArgumentType.STRING,
                            defaultValue: 'user',
                        }
                    }
                },
            ],
        };
    }

    openSocket (args) {
	const WS = args.WS;
    	if (this.isRunning == false) {
    		console.log("CloudLink API v" + vers + " | Opening socket...");
    		this.mWS = new WebSocket(WS);
    		const self = this;
    		this.mWS.onerror = function(){
    			self.isRunning = false;
    			console.log("CloudLink API v" + vers + " | Failed to connect to socket.");
    		};
    		this.mWS.onopen = function(){
    			self.isRunning = true;
			this.mWS.send("%_con\n" + this.ID);
    			console.log("CloudLink API v" + vers + " | Connected to socket successfully.");
    		}
    	}
    	else{
    		console.log("CloudLink API v" + vers + " | Socket already open, no action taken.");
		return "Socket already open, no action taken.";
    	}
    }

    closeSocket () {
        if (this.isRunning == true) {
    		console.log("CloudLink API v" + vers + " | Closing socket...");
    		this.mWS.close(1000,'The script told me to disconnect :(');
		console.log("CloudLink API v" + vers + " | Socket closed successfully.");
    		this.isRunning = false;
		return "Socket closed successfully.";
    	}
    	else{
    		console.log("CloudLink API v" + vers + " | Attempted to close socket, but socket already closed.");
		return "Socket already closed, no action taken.";
    	}
    }

   	getSocketState () {
   		if (this.isRunning){
   			var response = this.mWS.readyState;
   			if (response == 2 || response == 3) {
   				this.isRunning = false;
   				console.log("CloudLink API v" + vers + " | Socket closed unexpectedly.")
   			}
   		}
   		return this.isRunning;
   	}

   	sendDataGlobalStream (args) {
   		if (this.isRunning == true) {
   			this.mWS.send('@a\n' + args.DATA);
			return "Sent data successfully.";
   		}
		else {
			return "Socket not open, no action taken.";
		}
   	}
	
	sendDataPrivateStream (args) {
   		if (this.isRunning == true) {
   			this.mWS.send(args.ID + '\n' + args.DATA);
			return "Sent data successfully.";
   		}
		else {
			return "Socket not open, no action taken.";
		}
   	}

   	fetchDataGlobalStream (args) {
   		if (this.isRunning == true) {
   			this.mWS.send("%_fetch\n" + args.ID);
   			const self = this;
   			//Load response
   			var message = this.mWS.onmessage = function(event){
   				self.socketDataGlobalStream = String(event.data);
				self.socketDataGlobalStream = self.socketDataGlobalStream.slice(1, -1)
   			};
   		}
		else {
			return "Socket not open, no action taken.";
		}
   	}

   	getSocketDataGlobalStream () {
		return this.socketDataGlobalStream;
   	}
	
	getSocketDataPrivateStream() {
		const self = this;
		var str = this.socketDataPrivateStream;
		var rt = str.split("\n");
		if (rt[0] == this.ID) {
			return rt[1];
			self.socketDataPrivateCached = rt[1];
		};
		else {
			return this.socketDataPrivateCached;
		}
	}
	
	fetchDataPrivateStream (args) {
   		if (this.isRunning == true) {
   			this.mWS.send("%_fetch\n@a");
   			const self = this;
   			//Load response
   			var message = this.mWS.onmessage = function(event){
   				self.socketDataGlobalStream = String(event.data);
				self.socketDataGlobalStream = self.socketDataGlobalStream.slice(1, -1)
   			};
   		}
		else {
			return "Socket not open, no action taken.";
		}
   	}
}

Scratch.extensions.register(new cloudlink());
console.log("CloudLink API v" + vers + " | Ready!");
