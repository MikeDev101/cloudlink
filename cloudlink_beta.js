// MikeDEV's CloudLink API
// BETA RELEASE - DO NOT USE IN PRODUCTION!!!
// Built upon KingdomPi's Scratch-websockets repo.
// See https://github.com/KingdomPy/scratch_websockets/blob/master/index.js for the original script!
// DO NOT USE ON OLDER WEB BROWSERS! CloudLink is designed to run best on a modern web browser.

const vers = '1.2 B8.8_4';

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
    this.myUserID = []; // List for storing client's user IDs to multiple connection streams.
    this.userIDList = ['%MS%;']; // List for storing user IDs from multiple connection streams.
    this.globalData = ['Apple']; // List for indexing websocket connection streams, a link's GLOBAL data stream.
    this.privateData = ['Banana']; // List for indexing websocket connection streams, a link's PRIVATE data stream.
    this.linkIDs = ['Link A']; // List for indexing multiple websocket connection streams.
    this.links = []; // List for accessing websocket connection objects.
    this.linkStates = {'Link A':2}; // Dictionary for indexing multiple websocket connection states.
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
              defaultValue: 'Link A',
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
              defaultValue: 'Link A',
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
              defaultValue: 'Link A',
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
          opcode: 'isLinkConnected', // Returns true or false if a link is connected or not.
          blockType: BlockType.BOOLEAN,
          arguments: {
            linkID: {
              defaultValue: 'Link A',
              type: ArgumentType.STRING
            }
          },
          text: 'Is [linkID] Connected?'
        },
        {
          opcode: 'getNewDataOnLink', // Returns true if a link receives new data on it's global/private data streams.
          blockType: BlockType.BOOLEAN,
          arguments: {
            linkID: {
              defaultValue: 'Link A',
              type: ArgumentType.STRING
            }
          },
          text: 'Got new data from [linkID]?'
        },
        {
          opcode: 'connectToServer', // Spawns a new WebSocket object in the Links list, adds a new Link ID to the Link ID list, and spawns a connection.
          blockType: BlockType.COMMAND,
          arguments: {
            serverIP: {
              defaultValue: 'ws://127.0.0.1:3000/',
              type: ArgumentType.STRING
            },
            linkID: {
              defaultValue: 'Link A',
              type: ArgumentType.STRING
            }
          },
          text: 'Connect to [serverIP] as [linkID]'
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
              defaultValue: 'Link A',
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
              defaultValue: 'Link A',
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
              defaultValue: 'Link A',
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
              defaultValue: 'Link A',
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
              defaultValue: 'Link A',
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
  return "E: Link not found or disconnected!"
  }
}

getLinksList (args){
  return this.linkIDs;
}

connectToServer (args){
  const serverIP = args.serverIP;
  const linkID = args.linkID;
  // TODO: Figure out how to add a websocket object to a list
  return;
}

getStatusOfLink (args){
  const linkID = args.linkID;
  if (this.linkIDs.indexOf(linkID) != -1) {
    return this.linkStates[linkID]
  } else {
  return "E: Link not found or disconnected!"
  }
}

isLinkConnected (args){
  const linkID = args.linkID;
  if (this.linkIDs.indexOf(linkID) != -1) {
    return (this.linkStates[linkID] == 2)
  } else {
  return false
  }
}
  
getLinkData (args){
  const linkID = args.linkID;
  const streamType = args.streamType;
  if (this.linkIDs.indexOf(linkID) != -1) {
    console.log(streamType)
    if (streamType == "Global") {
      return this.globalData[(this.linkIDs.indexOf(linkID))]
    } else if (streamType == "Private") {
      return this.privateData[(this.linkIDs.indexOf(linkID))]
    } else {
      return "E: An error occured while reading const streamType!"
    }
  } else {
  return "E: Link not found or disconnected!"
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
  
  return;
}
  
setMyUserID (args){
  const linkID = args.linkID;
  const userID = args.userID;
  
  return;
}
getNewDataOnLink (args){
  const linkID = args.linkID;
  
  return;
}
}

Scratch.extensions.register(new cloudlink());
console.log("CloudLink API v" + vers + " | Ready!");
console.log("CloudLink API v" + vers + " | WARNING! You are using a BETA release of the CloudLink API Client! It may be unstable or buggy. YOU HAVE BEEN WARNED...");
