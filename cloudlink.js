// MikeDEV's CloudLink API
// Version 1.1b - Built upon KingdomPi's Scratch-websockets repo.
// See https://github.com/KingdomPy/scratch_websockets/blob/master/index.js for the original script!
// DO NOT USE ON OLDER WEB BROWSERS! CloudLink is designed to run best on a modern web browser.
const vers = '1.1c';

const blockIconURI = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFAAAABQCAYAAACOEfKtAAAE9ElEQVR4Xu2aS4gcVRSGv9MOjSJowI0RRONODDKj0tUDMzgjggohKgRFETIRcaUwoqAIkkR04QMi6saFzEhIBAMad7rK+JyujpCIoBsfCcTHMiIIMdpHqh+T6Zl6dZ3qeYRzl133P3Xq6//ec++tEryZCIhJ7WIcoNEEDtABGgkY5e5AB2gkYJS7Ax2gkYBR7g50gEYCRrk70AEaCRjl7kAHaCRglLsDHaCRgFHuDnSARgJGuTvQARoJGOXuQAdoJGCUuwM3BMATuoVzHECY6eZzEmEPNTlpzK88eaj3Abu7Ad8jkKNlBLc7MIL3D8eA0RUJnUWY3hAQQ51fBq+X5j4C2W+FaAOYDK+Tl7BATaatSZr0DZ1FOBAbQ5mnLnss8YsDzILXyyqQ4vewPFlPG+op4LrEUEaIxR4uLzz4k0C2lMGhcIxQNYd2P4Hsy9FvVZfBAeaHF92scGJFHiZWE2pULO7NjNcpetFcOVAbDOBg8D4jkKmBshlG507O0TC+MjN8AYj5AQ4G71uqTDEmZzOTXosOTR1FWRgGxHwANzO83h80JIj5AOadR2BjOW+lu4cAMRtg/CI0buBtbHhDcmI6wLLhhfowMAH8wggfcav8mDgFHtc7abETuLo9f40wz23yd2z/ht4M7KLCTcAiIxzmFvktMXaJTkwGWCa8pj6IMgdc1vdQwhvU5Km+3xp6BcIHwF19vyv/Ao9Sl4N9v4f6FvBEDKxnCeTVYUOMB1gmvON6Ay1+Sim2zxHIK0vXm/oOyuOJ/YWt1OSP9vVQnwTeTOyr3EFdon16fCvBiasBlgkvSruhryM8nbpa6W33mhoN199T+yp7qcuLXYBZu4wjBPJAajwjxH6A+eGdpspornVeqD8D2zKgTFKXLwn1IeBwxtIwJJA6i3ojFb7P6HuOQC7NXGo2daY7xWR27R7TLe1Y+gEaAqUMk19RrsnI7G4C+ZROkTmU2ldoUpOAr3Q7I3yXEfc8gVQzqXTWuSeA6zP7Rku1QJaO7lYP4bIhNnUOXTpojc/vEi5vV9hvdCv/kVw9O+oL++vsg4KjBHJ/JpRQo13K7Zn9Yta58UWkTIgNnUD4IiW5twkkKgadFuq77Wqb1JRrqcuZ9uWmPoPyWmJf4R5q8kkqmPzTVuw6N3kZUybEUF8Gno95kM85zw4m5K9lAK8CjgBxB7GPEUgE+EJr6EGER1bFVl6iLi8ME14UO30hPQjEFtOMSzQU4tvXOkaF3VSYRIkKy4cE8n5i/1B3oOyk0l5IH6PKXGLRCnUSYRfK9vZCusUhxuWHYcPLBtgZJnkr1MZ5B5I1mRmH7fLw2Xvhiw1iifDyObCH+2JwYsnwBgO42Z04BHiDA9ysEIcErxjAwSCeIpD0bVzWhG+9Hmr0tm1vjjCFzjPzFZG4u+edE4Wxdf06IXu3Ej1dIXjFHThIYWmxjXGJ3oqtfeuctER73LRWGJ4dYPZwXv9Xm6FGbwaTXmma4JUDMBniaVpMrZv7ep5b1Ckq7Y+fVjYzvPIARpE6ic52v9JaoMpsrvPCtRjYnU/bojO8nhM/pspMGfkVLyJr8eCb4B4O0PgnOUAHaCRglLsDHaCRgFHuDnSARgJGuTvQARoJGOXuQAdoJGCUuwMdoJGAUe4OdIBGAka5O9ABGgkY5e5AB2gkYJS7Ax2gkYBR7g50gEYCRvn/QEDeYP09rHoAAAAASUVORK5CYII=';
const menuIconURI = blockIconURI;

var myName = "";
var gotNewGlobalData = false;
var gotNewPrivateData = false;

class cloudlink {
    constructor(runtime, extensionId) {
        this.runtime = runtime;
        this.sGData = "";
        this.sPData = "";
        this.isRunning = false;
        this.status = 0; // Ready value
        this.userNames = "";
    }

    static get STATE_KEY() {
        return 'Scratch.websockets';
    }

    getInfo() {
        return {
            id: 'cloudlink',
            name: ('CloudLink v' + vers),
            blockIconURI: blockIconURI,
            color1: '#054c63',
            color2: '#054c63',
            color3: '#043444',
            blocks: [{
                    opcode: 'getGData',
                    blockType: Scratch.BlockType.REPORTER,
                    text: 'Socket Data (Global)',
                },
                {
                    opcode: 'getPData',
                    blockType: Scratch.BlockType.REPORTER,
                    text: 'Socket Data (Private)',
                },
                {
                    opcode: 'getStatus',
                    blockType: Scratch.BlockType.REPORTER,
                    text: 'Status',
                },
                {
                    opcode: 'getCNames',
                    blockType: Scratch.BlockType.REPORTER,
                    text: 'Connected Users',
                },
                {
                    opcode: 'getMyName',
                    blockType: Scratch.BlockType.REPORTER,
                    text: 'My Username',
                },
                {
                    opcode: 'getSocketState',
                    blockType: Scratch.BlockType.BOOLEAN,
                    text: 'Connected?',
                },
                {
                    opcode: 'isNewGlobalData',
                    blockType: Scratch.BlockType.BOOLEAN,
                    text: 'Got New Data (Global)?',
                },
                {
                    opcode: 'isNewPrivateData',
                    blockType: Scratch.BlockType.BOOLEAN,
                    text: 'Got New Data (Private)?',
                },
                {
                    opcode: 'parseJSON',
                    blockType: Scratch.BlockType.REPORTER,
                    text: '[PATH] of [JSON_STRING]',
                    arguments: {
                        PATH: {
                            type: Scratch.ArgumentType.STRING,
                            defaultValue: 'fruit/apples'
                        },
                        JSON_STRING: {
                            type: Scratch.ArgumentType.STRING,
                            defaultValue: '{"fruit": {"apples": 2, "bananas": 3}, "total_fruit": 5}'
                        }
                    }
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
                    opcode: 'sendGData',
                    blockType: Scratch.BlockType.COMMAND,
                    text: 'Send [DATA] (Global)',
                    arguments: {
                        DATA: {
                            type: Scratch.ArgumentType.STRING,
                            defaultValue: 'thing',
                        },
                    },
                },
                {
                    opcode: 'sendPData',
                    blockType: Scratch.BlockType.COMMAND,
                    text: 'Send [DATA] to [ID] (Private)',
                    arguments: {
                        DATA: {
                            type: Scratch.ArgumentType.STRING,
                            defaultValue: 'thing',
                        },
                        ID: {
                            type: Scratch.ArgumentType.STRING,
                            defaultValue: 'a name',
                        },
                    },
                },
                {
                    opcode: 'setMyName',
                    blockType: Scratch.BlockType.COMMAND,
                    text: 'Set [NAME] as my username',
                    arguments: {
                        NAME: {
                            type: Scratch.ArgumentType.STRING,
                            defaultValue: 'a name',
                        },
                    },
                },
                {
                    opcode: 'resetGotNewGlobalData',
                    blockType: Scratch.BlockType.COMMAND,
                    text: 'Reset Got New Data (Global)',
                },
                {
                    opcode: 'resetGotNewPrivateData',
                    blockType: Scratch.BlockType.COMMAND,
                    text: 'Reset Got New Data (Private)',
                },
                {
                    opcode: 'refreshConnectedUsersList',
                    blockType: Scratch.BlockType.COMMAND,
                    text: 'Refresh User List',
                },
            ],
        };
    }
    openSocket(args) {
        const WSS = args.WSS; // Begin the main updater scripts
        if (this.isRunning == false) {
            const self = this;
            self.status = 1;
            console.log("CloudLink API v" + vers + " | Establishing connection...");
            this.wss = new WebSocket(WSS);
            this.wss.onopen = function(e) {
                self.isRunning = true;
                self.status = 2; // Connected OK value
                console.log("CloudLink API v" + vers + " | Connected.");
            };
            this.wss.onmessage = function(event) {
                var obj = JSON.parse(event.data);
                if (obj["type"] == "gs") {
                    self.sGData = String(obj["data"]);
                    gotNewGlobalData = true;
                } else if (obj["type"] == "ps") {
                    if (String(obj["id"]) == String(myName)) {
                        self.sPData = String(obj["data"]);
                        gotNewPrivateData = true;
                    };
                } else if (obj["type"] == "ul") {
                    self.userNames = String(obj["data"]);
                } else {
                    console.log("CloudLink API v" + vers + " | Error! Unknown command: " + String(obj));
                };
            };
            this.wss.onclose = function(event) {
                self.userNames = "";
                self.sGData = "";
                self.sPData = "";
                self.isRunning = false;
                gotNewGlobalData = false;
                gotNewPrivateData = false;
                myName = "";
                if (event.wasClean) {
                    self.status = 3; // Disconnected OK value
                    console.log("CloudLink API v" + vers + " | Disconnected. :)");
                } else {
                    self.status = 4; // Connection lost value
                    console.log("CloudLink API v" + vers + " | Lost connection to the server. :(");
                };
            };
        } else {
            return ("Connection already established.");
        };
    } // end the updater scripts

    closeSocket() {
        const self = this;
        if (this.isRunning == true) {
            this.wss.send("<%ds>\n" + myName); // send disconnect command in header before shutting down link
            this.wss.close(1000);
            self.isRunning = false;
            myName = "";
            gotNewGlobalData = false;
            gotNewPrivateData = false;
            self.userNames = "";
            self.sGData = "";
            self.sPData = "";
            self.status = 3; // Disconnected OK value
            return ("Connection closed.");
        } else {
            return ("Connection already closed.");
        };
    }

    getSocketState() {
        return this.isRunning;
    }

    sendGData(args) {
        if (this.isRunning == true) {
            this.wss.send("<%gs>\n" + myName + "\n" + args.DATA); // begin packet data with global stream idenifier in the header
            return "Sent data successfully.";
        } else {
            return "Connection closed, no action taken.";
        }
    }

    sendPData(args) {
        if (myName != "") {
            if (this.isRunning == true) {
                this.wss.send("<%ps>\n" + myName + "\n" + args.ID + "\n" + args.DATA); // begin packet data with global stream idenifier in the header
                return "Sent data successfully.";
            } else {
                return "Connection closed, no action taken.";
            }
        } else {
            return "Username not set, no action taken.";
        };
    }

    getGData() {
        return this.sGData;
    }

    getPData() {
        return this.sPData;
    }

    getStatus() {
        return this.status;
    }

    getCNames() {
        return this.userNames;
    }

    getMyName() {
        return myName;
    }

    setMyName(args) {
        if (myName == "") {
            if (this.isRunning == true) {
                this.wss.send("<%sn>\n" + args.NAME); // begin packet data with setname command in the header
                myName = args.NAME;
                return "Set username on server successfully.";
            } else {
                return "Connection closed, no action taken.";
            }
        } else {
            return "Username already set!";
        };
    }
    parseJSON({
        PATH,
        JSON_STRING
    }) {
        try {
            const path = PATH.toString().split('/').map(prop => decodeURIComponent(prop));
            if (path[0] === '') path.splice(0, 1);
            if (path[path.length - 1] === '') path.splice(-1, 1);
            let json;
            try {
                json = JSON.parse(' ' + JSON_STRING);
            } catch (e) {
                return e.message;
            }
            path.forEach(prop => json = json[prop]);
            if (json === null) return 'null';
            else if (json === undefined) return '';
            else if (typeof json === 'object') return JSON.stringify(json);
            else return json.toString();
        } catch (err) {
            return '';
        }
    }
    isNewGlobalData() {
        return gotNewGlobalData;
    }
    isNewPrivateData() {
        return gotNewPrivateData;
    }
    resetGotNewGlobalData() {
        gotNewGlobalData = false;
    }
    resetGotNewPrivateData() {
        gotNewPrivateData = false;
    }
    refreshConnectedUsersList() {
        if (this.isRunning == true) {
            this.wss.send("<%rf>\n"); // begin packet data with global stream idenifier in the header
            return "Request sent.";
        } else {
            return "Connection closed, no action taken.";
        }
    }
}

Scratch.extensions.register(new cloudlink());
console.log("CloudLink API v" + vers + " | Ready!");
