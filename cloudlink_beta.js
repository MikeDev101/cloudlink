// MikeDEV's CloudLink API
// BETA RELEASE - DO NOT USE IN PRODUCTION!!!
// Built upon KingdomPi's Scratch-websockets repo.
// See https://github.com/KingdomPy/scratch_websockets/blob/master/index.js for the original script!
// DO NOT USE ON OLDER WEB BROWSERS! CloudLink is designed to run best on a modern web browser.

const vers = '1.3 B3';

const blockIconURI = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFAAAABQCAYAAACOEfKtAAAE9ElEQVR4Xu2aS4gcVRSGv9MOjSJowI0RRONODDKj0tUDMzgjggohKgRFETIRcaUwoqAIkkR04QMi6saFzEhIBAMad7rK+JyujpCIoBsfCcTHMiIIMdpHqh+T6Zl6dZ3qeYRzl133P3Xq6//ec++tEryZCIhJ7WIcoNEEDtABGgkY5e5AB2gkYJS7Ax2gkYBR7g50gEYCRrk70AEaCRjl7kAHaCRglLsDHaCRgFHuDnSARgJGuTvQARoJGOXuQAdoJGCUuwM3BMATuoVzHECY6eZzEmEPNTlpzK88eaj3Abu7Ad8jkKNlBLc7MIL3D8eA0RUJnUWY3hAQQ51fBq+X5j4C2W+FaAOYDK+Tl7BATaatSZr0DZ1FOBAbQ5mnLnss8YsDzILXyyqQ4vewPFlPG+op4LrEUEaIxR4uLzz4k0C2lMGhcIxQNYd2P4Hsy9FvVZfBAeaHF92scGJFHiZWE2pULO7NjNcpetFcOVAbDOBg8D4jkKmBshlG507O0TC+MjN8AYj5AQ4G71uqTDEmZzOTXosOTR1FWRgGxHwANzO83h80JIj5AOadR2BjOW+lu4cAMRtg/CI0buBtbHhDcmI6wLLhhfowMAH8wggfcav8mDgFHtc7abETuLo9f40wz23yd2z/ht4M7KLCTcAiIxzmFvktMXaJTkwGWCa8pj6IMgdc1vdQwhvU5Km+3xp6BcIHwF19vyv/Ao9Sl4N9v4f6FvBEDKxnCeTVYUOMB1gmvON6Ay1+Sim2zxHIK0vXm/oOyuOJ/YWt1OSP9vVQnwTeTOyr3EFdon16fCvBiasBlgkvSruhryM8nbpa6W33mhoN199T+yp7qcuLXYBZu4wjBPJAajwjxH6A+eGdpspornVeqD8D2zKgTFKXLwn1IeBwxtIwJJA6i3ojFb7P6HuOQC7NXGo2daY7xWR27R7TLe1Y+gEaAqUMk19RrsnI7G4C+ZROkTmU2ldoUpOAr3Q7I3yXEfc8gVQzqXTWuSeA6zP7Rku1QJaO7lYP4bIhNnUOXTpojc/vEi5vV9hvdCv/kVw9O+oL++vsg4KjBHJ/JpRQo13K7Zn9Yta58UWkTIgNnUD4IiW5twkkKgadFuq77Wqb1JRrqcuZ9uWmPoPyWmJf4R5q8kkqmPzTVuw6N3kZUybEUF8Gno95kM85zw4m5K9lAK8CjgBxB7GPEUgE+EJr6EGER1bFVl6iLi8ME14UO30hPQjEFtOMSzQU4tvXOkaF3VSYRIkKy4cE8n5i/1B3oOyk0l5IH6PKXGLRCnUSYRfK9vZCusUhxuWHYcPLBtgZJnkr1MZ5B5I1mRmH7fLw2Xvhiw1iifDyObCH+2JwYsnwBgO42Z04BHiDA9ysEIcErxjAwSCeIpD0bVzWhG+9Hmr0tm1vjjCFzjPzFZG4u+edE4Wxdf06IXu3Ej1dIXjFHThIYWmxjXGJ3oqtfeuctER73LRWGJ4dYPZwXv9Xm6FGbwaTXmma4JUDMBniaVpMrZv7ep5b1Ckq7Y+fVjYzvPIARpE6ic52v9JaoMpsrvPCtRjYnU/bojO8nhM/pspMGfkVLyJr8eCb4B4O0PgnOUAHaCRglLsDHaCRgFHuDnSARgJGuTvQARoJGOXuQAdoJGCUuwMdoJGAUe4OdIBGAka5O9ABGgkY5e5AB2gkYJS7Ax2gkYBR7g50gEYCRvn/QEDeYP09rHoAAAAASUVORK5CYII=';
const menuIconURI = blockIconURI;

// created by scratch3-extension generator
const ArgumentType = Scratch.ArgumentType;
const BlockType = Scratch.BlockType;
const formatMessage = Scratch.formatMessage;
const log = Scratch.log;

class cloudlink {
  constructor (runtime){
    this.runtime = runtime;
    this.isRunning = false; // Defines if the primary WebSocket connection is established.
    this.myUserID = []; // List for storing client's user IDs to multiple connection streams.
    this.userIDList = []; // List for storing user IDs from multiple connection streams.
    this.globalData = ['']; // List for indexing websocket connection streams, a link's GLOBAL data stream.
    this.privateData = ['']; // Array for indexing websocket connection streams, a link's PRIVATE data stream.
    this.linkIDs = ['%MS%']; // Array for indexing multiple link connection streams, provided by the API server.
    this.linkStates = {'%MS%':{'status':0, 'newG':false, 'newP':false}}; // Dictionary for indexing multiple link connection states.
  }

  getInfo (){
    return {
      id: 'cloudlink',
      name: ('CloudLink BETA'),
      color1: '#054c63',
      color2: '#054c63',
      color3: '#043444',
      menuIconURI: menuIconURI,
      blockIconURI: blockIconURI,
      docsURL: 'https://github.com/MikeDev101/cloudlink/wiki',
      blocks: [
        {
          opcode: 'getStatusOfLink', // Reports status values 0-4 for a link, if a connection attempt has been made.
          blockType: BlockType.REPORTER,
          arguments: {
            linkID: {
              defaultValue: '%MS%',
              type: ArgumentType.STRING
            }
          },
          text: 'Status of [linkID]'
        },
        {
          opcode: 'getUserIDListOfLink', // Reports the User ID list from a link.
          blockType: BlockType.REPORTER,
          arguments: {
            linkID: {
              defaultValue: '%MS%',
              type: ArgumentType.STRING
            }
          },
          text: 'User ID list of [linkID]'
        },
        {
          opcode: 'getLinksList', // Reports a list of all running links.
          blockType: BlockType.REPORTER,
          text: 'Running Links'
        },
        {
          opcode: 'getLinkData', // Returns data from the global/private data streams from a link.
          blockType: BlockType.REPORTER,
          arguments: {
            linkID: {
              defaultValue: '%MS%',
              type: ArgumentType.STRING
            },
            streamType: {
              defaultValue: '',
              type: ArgumentType.NUMBER,
              menu: 'streamType'
            }
          },
          text: '[streamType] Data from [linkID]'
        },
        {
          opcode: 'parseJSON',
          blockType: BlockType.REPORTER,
          text: '[PATH] of [JSON_STRING]',
          arguments: {
            PATH: {
              type: ArgumentType.STRING,
              defaultValue: 'fruit/apples'
            },
            JSON_STRING: {
              type: ArgumentType.STRING,
              defaultValue: '{"fruit": {"apples": 2, "bananas": 3}, "total_fruit": 5}'
            }
          }
        },
        {
          opcode: 'isLinkConnected', // Returns true or false if a link is connected or not.
          blockType: BlockType.BOOLEAN,
          arguments: {
            linkID: {
              defaultValue: '%MS%',
              type: ArgumentType.STRING
            }
          },
          text: 'Is [linkID] Connected?'
        },
        {
          opcode: 'gotNewDataOnLink', // Returns true if a link receives new data on it's global/private data streams.
          blockType: BlockType.BOOLEAN,
          arguments: {
            linkID: {
              defaultValue: '%MS%',
              type: ArgumentType.STRING
            },
            streamType: {
              defaultValue: '',
              type: ArgumentType.NUMBER,
              menu: 'streamType'
            }
          },
          text: 'Got new [streamType] data from [linkID]?'
        },
        {
          opcode: 'connectToServer', // Spawns the main WebSocket session.
          blockType: BlockType.COMMAND,
          arguments: {
            serverIP: {
              defaultValue: 'ws://127.0.0.1:3000/',
              type: ArgumentType.STRING
            },
          },
          text: 'Connect to Server [serverIP]'
        },
        {
          opcode: 'connectToLink', // Connects to a server linked with the currently connected API server.
          blockType: BlockType.COMMAND,
          arguments: {
            linkID: {
              defaultValue: '%MS%',
              type: ArgumentType.STRING
            }
          },
          text: 'Connect to Link [linkID]'
        },
        {
          opcode: 'setMyUserID', // If a connection is established successfully on a link, this sets the client's User ID on that link, which enables private data streams.
          blockType: BlockType.COMMAND,
          arguments: {
            userID: {
              defaultValue: 'Somebody',
              type: ArgumentType.STRING
            },
            linkID: {
              defaultValue: '%MS%',
              type: ArgumentType.STRING
            }
          },
          text: 'Set my User ID as [userID] on [linkID]'
        },
        {
          opcode: 'sendPacketGlobal', // Transmit packet over the global data stream on a live link.
          blockType: BlockType.COMMAND,
          arguments: {
            packetData: {
              defaultValue: 'Bananas',
              type: ArgumentType.STRING
            },
            linkID: {
              defaultValue: '%MS%',
              type: ArgumentType.STRING
            }
          },
          text: 'Send [packetData] on [linkID] (Global)'
        },
        {
          opcode: 'sendPacketPrivate', // Transmit packet over the private data stream on a live link.
          blockType: BlockType.COMMAND,
          arguments: {
            packetData: {
              defaultValue: 'Apples',
              type: ArgumentType.STRING
            },
            linkID: {
              defaultValue: '%MS%',
              type: ArgumentType.STRING
            },
            userID: {
              defaultValue: 'Someone',
              type: ArgumentType.STRING
            }
          },
          text: 'Send [packetData] to [userID] on [linkID] (Private)'
        },
        {
          opcode: 'refreshUserlist', // Transmits a refresh User ID list request to the server on a live link.
          blockType: BlockType.COMMAND,
          arguments: {
            linkID: {
              defaultValue: '%MS%',
              type: ArgumentType.STRING
            }
          },
          text: 'Refresh User ID List on [linkID]'
        },
        {
          opcode: 'disconnectFromLink', // Sends a disconnect command to the server on a live link, and ends the session. It closes the WebSocket connection, removes the WebSocket object from the Links list, and removes the Link ID from the Link IDs list.
          blockType: BlockType.COMMAND,
          arguments: {
            linkID: {
              defaultValue: '%MS%',
              type: ArgumentType.STRING
            }
          },
          text: 'Disconnect [linkID]'
        },
        {
          opcode: 'disconnectAllLinks', // Sends a disconnect command to all live links, and ends all sessions.
          blockType: BlockType.COMMAND,
          text: 'Disconnect All Links'
        }
      ],
      menus: {
        streamType: {
          items: ['Global', 'Private']
        },
      }
    }
  }

getUserIDListOfLink (args){
  const linkID = args.linkID;
  if (this.linkIDs.indexOf(linkID) != -1) {
    return this.userIDList[(this.linkIDs.indexOf(linkID))]
  } else {
  return ""
  }
}

getLinksList (args){
  return this.linkIDs.toString();
}

connectToServer (args){
  const serverIP = args.serverIP;
  const self = this;
  // TODO: Spawn main websocket connection
  console.log("CloudLink API v" + vers + " | Connecting...");
  if (this.isRunning == false) {
    self.isRunning = true; // Enable engine
    // Spawn connection
    this.wss = new WebSocket(serverIP);
    // Create default link and spawn state data
    self.linkIDs = '%MS%;';
    self.linkStates['%MS%'] = {'status':1, 'newG':false, 'newP':false};
    this.wss.onopen = function(e) {
      self.isRunning = true;
      // Update state to 2 (Connected) if OK
      self.linkStates['%MS%']['status'] = 2;
      console.log("CloudLink API v" + vers + " | Connected. ");
    };
    this.wss.onmessage = function(event) {
      var obj = JSON.parse(event.data);
      // TODO: Update values when a message is received
    };
    this.wss.onclose = function(event) {
      if (event.wasClean) { // Check if the disconnect was clean
        // Reset new data values and set status to 3 (Disconnected OK)
        self.linkStates['%MS%'] = {'status':3, 'newG':false, 'newP':false};
        self.isRunning = false;
        console.log("CloudLink API v" + vers + " | Disconnected, and everything's OK. ");
      } else {
        // Reset new data values and set status to 4 (Disconnected ERR)
        self.linkStates['%MS%'] = {'status':4, 'newG':false, 'newP':false};
        self.isRunning = false;
        console.log("CloudLink API v" + vers + " | Disconnected, But it was because of an error. ");
      }
    };
  } else {
    return "Connection to server already established!"
  }
}

connectToLink (args){
  const linkID = args.linkID;
  if (this.isRunning == true) {
    return;
    // TODO: Check if a link (software server connected to the API locally) exists on the API server, and connect to it.
  } else {
    return 'Oops, the WebSocket is not connected. Run the "Connect to Server" block to connect!';
  }
}

getStatusOfLink (args){
  const linkID = args.linkID;
  if (this.linkIDs.indexOf(linkID) != -1) {
    return (this.linkStates[linkID])['status']
  } else {
  return ""
  }
}

isLinkConnected (args){
  const linkID = args.linkID;
  if (this.linkIDs.indexOf(linkID) != -1) {
    return ((this.linkStates[linkID])['status'] == 2)
  } else {
  return false
  }
}

getLinkData (args){
  const linkID = args.linkID;
  const streamType = args.streamType;
  if (this.linkIDs.indexOf(linkID) != -1) {
    if (streamType == "Global") {
      return this.globalData[(this.linkIDs.indexOf(linkID))]
    } else if (streamType == "Private") {
      return this.privateData[(this.linkIDs.indexOf(linkID))]
    } else {
      return ""
    }
  } else {
  return ""
  }
}

sendPacketGlobal (args){
  const packetData = args.packetData;
  const linkID = args.linkID;
  const streamType = args.streamType;

  return;
}

sendPacketPrivate (args) {
  const packetData = args.packetData;
  const linkID = args.linkID;
  const userID = args.userID;
  const streamType = args.streamType;

  return;
}

refreshUserlist (args){
  const linkID = args.linkID;

  return;
}

disconnectFromLink (args){
  const linkID = args.linkID;
  
  return;
}

disconnectAllLinks (args){
  const self = this;
  if (this.isRunning == true) {
    //if () { TODO: Finish this
    //}
    this.wss.send("<%ds>\n"+);
  }
  return;
}
  
setMyUserID (args){
  const linkID = args.linkID;
  const userID = args.userID;
  
  return;
}

gotNewDataOnLink (args){
  const linkID = args.linkID;
  const streamType = args.streamType;
  if (this.linkIDs.indexOf(linkID) != -1) {
    if (streamType == "Global") {
      return (this.linkStates[linkID])['newG']
    } else if (streamType == "Private") {
      return (this.linkStates[linkID])['newP']
    } else {
      return ""
    }
  } else {
  return ""
  }
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
}

Scratch.extensions.register(new cloudlink());
console.log("CloudLink API v" + vers + " | Ready! However, you are using a BETA release of the extension. It may be unstable or buggy. YOU HAVE BEEN WARNED...");
