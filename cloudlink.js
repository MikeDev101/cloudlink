// MikeDEV's CloudLink API
// Version 0.1.8 - Built upon KingdomPi's Scratch-websockets repo.
// See https://github.com/KingdomPy/scratch_websockets/blob/master/index.js for the original script!
// DO NOT USE ON OLDER WEB BROWSERS! CloudLink is designed to run best on a modern web browser.
const vers = '0.1.8';

const blockIconURI = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFAAAABQCAYAAACOEfKtAAAE9ElEQVR4Xu2aS4gcVRSGv9MOjSJowI0RRONODDKj0tUDMzgjggohKgRFETIRcaUwoqAIkkR04QMi6saFzEhIBAMad7rK+JyujpCIoBsfCcTHMiIIMdpHqh+T6Zl6dZ3qeYRzl133P3Xq6//ec++tEryZCIhJ7WIcoNEEDtABGgkY5e5AB2gkYJS7Ax2gkYBR7g50gEYCRrk70AEaCRjl7kAHaCRglLsDHaCRgFHuDnSARgJGuTvQARoJGOXuQAdoJGCUuwM3BMATuoVzHECY6eZzEmEPNTlpzK88eaj3Abu7Ad8jkKNlBLc7MIL3D8eA0RUJnUWY3hAQQ51fBq+X5j4C2W+FaAOYDK+Tl7BATaatSZr0DZ1FOBAbQ5mnLnss8YsDzILXyyqQ4vewPFlPG+op4LrEUEaIxR4uLzz4k0C2lMGhcIxQNYd2P4Hsy9FvVZfBAeaHF92scGJFHiZWE2pULO7NjNcpetFcOVAbDOBg8D4jkKmBshlG507O0TC+MjN8AYj5AQ4G71uqTDEmZzOTXosOTR1FWRgGxHwANzO83h80JIj5AOadR2BjOW+lu4cAMRtg/CI0buBtbHhDcmI6wLLhhfowMAH8wggfcav8mDgFHtc7abETuLo9f40wz23yd2z/ht4M7KLCTcAiIxzmFvktMXaJTkwGWCa8pj6IMgdc1vdQwhvU5Km+3xp6BcIHwF19vyv/Ao9Sl4N9v4f6FvBEDKxnCeTVYUOMB1gmvON6Ay1+Sim2zxHIK0vXm/oOyuOJ/YWt1OSP9vVQnwTeTOyr3EFdon16fCvBiasBlgkvSruhryM8nbpa6W33mhoN199T+yp7qcuLXYBZu4wjBPJAajwjxH6A+eGdpspornVeqD8D2zKgTFKXLwn1IeBwxtIwJJA6i3ojFb7P6HuOQC7NXGo2daY7xWR27R7TLe1Y+gEaAqUMk19RrsnI7G4C+ZROkTmU2ldoUpOAr3Q7I3yXEfc8gVQzqXTWuSeA6zP7Rku1QJaO7lYP4bIhNnUOXTpojc/vEi5vV9hvdCv/kVw9O+oL++vsg4KjBHJ/JpRQo13K7Zn9Yta58UWkTIgNnUD4IiW5twkkKgadFuq77Wqb1JRrqcuZ9uWmPoPyWmJf4R5q8kkqmPzTVuw6N3kZUybEUF8Gno95kM85zw4m5K9lAK8CjgBxB7GPEUgE+EJr6EGER1bFVl6iLi8ME14UO30hPQjEFtOMSzQU4tvXOkaF3VSYRIkKy4cE8n5i/1B3oOyk0l5IH6PKXGLRCnUSYRfK9vZCusUhxuWHYcPLBtgZJnkr1MZ5B5I1mRmH7fLw2Xvhiw1iifDyObCH+2JwYsnwBgO42Z04BHiDA9ysEIcErxjAwSCeIpD0bVzWhG+9Hmr0tm1vjjCFzjPzFZG4u+edE4Wxdf06IXu3Ej1dIXjFHThIYWmxjXGJ3oqtfeuctER73LRWGJ4dYPZwXv9Xm6FGbwaTXmma4JUDMBniaVpMrZv7ep5b1Ckq7Y+fVjYzvPIARpE6ic52v9JaoMpsrvPCtRjYnU/bojO8nhM/pspMGfkVLyJr8eCb4B4O0PgnOUAHaCRglLsDHaCRgFHuDnSARgJGuTvQARoJGOXuQAdoJGCUuwMdoJGAUe4OdIBGAka5O9ABGgkY5e5AB2gkYJS7Ax2gkYBR7g50gEYCRvn/QEDeYP09rHoAAAAASUVORK5CYII=';
const menuIconURI = blockIconURI;

class cloudlink {
    constructor(runtime, extensionId) {
        this.runtime = runtime;
        this.sData = "";
        this.isRunning = false;
        this.status = "Ready";
    }

    static get STATE_KEY() {
        return 'Scratch.websockets';
    }

    getInfo() {
        return {
            id: 'cloudlink',
            name: 'CloudLink',
            blockIconURI: blockIconURI,
            color1: '#054c63',
            color2: '#054c63',
            color3: '#043444',
            blocks: [{
                    opcode: 'getData',
                    blockType: Scratch.BlockType.REPORTER,
                    text: 'Socket Data',
                },
                {
                    opcode: 'getStatus',
                    blockType: Scratch.BlockType.REPORTER,
                    text: 'Status',
                },
                {
                    opcode: 'getSocketState',
                    blockType: Scratch.BlockType.BOOLEAN,
                    text: 'Connected?',
                },
                {
                    opcode: 'openSocket',
                    blockType: Scratch.BlockType.COMMAND,
                    text: 'Connect to [WSS]',
                    arguments: {
                        WSS: {
                            type: Scratch.ArgumentType.STRING,
                            defaultValue: 'ws://127.0.0.1:3000/',
                        },
                    },
                },
                {
                    opcode: 'closeSocket',
                    blockType: Scratch.BlockType.COMMAND,
                    text: 'Disconnect',
                },
                {
                    opcode: 'sendData',
                    blockType: Scratch.BlockType.COMMAND,
                    text: 'Send [DATA]',
                    arguments: {
                        DATA: {
                            type: Scratch.ArgumentType.STRING,
                            defaultValue: 'thing',
                        },
                    },
                },
            ],
        };
    }
    openSocket(args) {
        const WSS = args.WSS;
        if (this.isRunning == false) {
            const self = this;
            self.status = "connecting";
            console.log("CloudLink API v" + vers + " | Attempting connection to server...");
            this.wss = new WebSocket(WSS);
            this.wss.onopen = function(e) {
                    self.isRunning = true;
                    self.status = "Connected";
                    console.log("CloudLink API v" + vers + " | Connected to server.");
            };
            this.wss.onmessage = function(event) {
                var tmp = String(event.data);
                self.sData = tmp.slice(1, -1);
            };
            this.wss.onclose = function(event) {
                if (event.wasClean) {
                    self.isRunning = false;
                    self.status = "Disconnected, OK";
                    console.log("CloudLink API v" + vers + " | Server has been cleanly disconnected. :)");
                } else {
                    self.isRunning = false;
                    self.status = "Disconnected, ERR";
                    console.log("CloudLink API v" + vers + " | Server unexpectedly disconnected. :(");
                };
            };
        } else {
            return ("Connection already established.");
        };
    }

    closeSocket() {
        const self = this;
        if (this.isRunning == true) {
            this.wss.send("<%ds>\n") // send disconnect command in header before shutting down link
            this.wss.close(1000);
            self.isRunning = false;
            self.status = "Disconnected, OK";
            return ("Connection closed.");
        } else {
            return ("Connection already closed.");
        };
    }

    getSocketState() {
        return this.isRunning;
    }

    sendData(args) {
   		if (this.isRunning == true) {
   			this.wss.send("<%ps>\n" + args.DATA); // begin packet data with public stream idenifier in the header
			return "Sent data successfully.";
   		}
		else {
			return "Connection closed, no action taken.";
		}
    }

    getData() {
        return this.sData;
    }

    getStatus() {
        return this.status;
    }
    
}

Scratch.extensions.register(new cloudlink());
console.log("CloudLink API v" + vers + " | Ready!");
