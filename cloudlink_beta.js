// MikeDEV's CloudLink API
// BETA RELEASE - DO NOT USE IN PRODUCTION!!!
// Built upon KingdomPi's Scratch-websockets repo.
// See https://github.com/KingdomPy/scratch_websockets/blob/master/index.js for the original script!
// DO NOT USE ON OLDER WEB BROWSERS! CloudLink is designed to run best on a modern web browser.

const vers = '1.2 B8';

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
    this.gotNewEvent = false; // Trigger for event hat block
    this.myUserID = []; // List for storing client's user IDs to multiple connection streams.
    this.userIDList = []; // List for storing user IDs from multiple connection streams.
    this.globalData = []; // List for indexing websocket connection streams, a link's GLOBAL data stream.
    this.privateData = []; // List for indexing websocket connection streams, a link's PRIVATE data stream.
    this.linkID = [] // List for indexing multiple websocket connection streams.
  }

  getInfo (){
    return {
      id: 'cloudlink',
      name: ('CloudLink v' + vers),
      color1: '#054c63',
      color2: '#054c63',
      color3: '#043444',
      menuIconURI: menuIconURI,
      blockIconURI: blockIconURI,
      blocks: [
        {
          opcode: 'getLinkData',
          blockType: BlockType.BOOLEAN,
          arguments: {
            linkID: {
              defaultValue: 'Link A',
              type: ArgumentType.STRING
            },
            streamType: {
              defaultValue: '',
              type: ArgumentType.STRING,
              menu: 'streamType'
            }
          },
          text: '[streamType] Data from Link ID: [linkID]'
        },
        {
          opcode: 'getLinkState',
          blockType: BlockType.BOOLEAN,
          arguments: {
            linkID: {
              defaultValue: 'Link A',
              type: ArgumentType.STRING
            }
          },
          text: 'Is Link ID: [linkID] Connected?'
        },
        {
          opcode: 'onEvent',
          blockType: BlockType.HAT,
          isEdgeActivated: this.gotNewEvent,
          arguments: {
            eventID: {
              defaultValue: '',
              type: ArgumentType.NUMBER,
              menu: 'eventType'
            },
            linkID: {
              defaultValue: 'Link A',
              type: ArgumentType.STRING
            }
          },
          text: 'When [eventID] Link ID: [linkID]'
        },
        {
          opcode: 'connectToServer',
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
          text: 'Connect to IP: [serverIP] as Link ID: [linkID]'
        },
        {
          opcode: 'getStatusOfLink',
          blockType: BlockType.REPORTER,
          arguments: {
            linkID: {
              defaultValue: 'Link A',
              type: ArgumentType.STRING
            }
          },
          text: 'Status for Link ID: [linkID]'
        },
        {
          opcode: 'sendPacketGlobal',
          blockType: BlockType.COMMAND,
          arguments: {
            packetData: {
              defaultValue: 'thing',
              type: ArgumentType.STRING
            },
            linkID: {
              defaultValue: 'Link A',
              type: ArgumentType.STRING
            }
          },
          text: 'Send Data: [packetData] Globally through Link ID: [linkID]'
        },
        {
          opcode: 'refreshUserlist',
          blockType: BlockType.COMMAND,
          arguments: {
            linkID: {
              defaultValue: 'Link A',
              type: ArgumentType.STRING
            }
          },
          text: 'Refresh userlist on Link ID: [linkID]'
        },
        {
          opcode: 'disconnectFromLink',
          blockType: BlockType.COMMAND,
          arguments: {
            linkID: {
              defaultValue: 'Link A',
              type: ArgumentType.STRING
            }
          },
          text: 'Disconnect Link ID: [linkID]'
        },
        {
          opcode: 'disconnectAllLinks',
          blockType: BlockType.COMMAND,
          text: 'Disconnect ALL Links'
        }
      ],
      menus: {
        streamType: {
          items: ['Global', 'Private']
        },
        eventType: {
          items: ['connected to', 'disconnected from', 'an error occurs on', 'a broadcast is received from']
        }
      }
    }
  }

onEvent (args, util){
  const eventID = args.eventID;
  const linkID = args.linkID;
  
  return "";
}

connectToServer (args, util){
  const serverIP = args.serverIP;
  const linkID = args.linkID;

  return "";
}

getStatusOfLink (args, util){
  const linkID = args.linkID;
  const self = this;
  this.gotNewEvent = true;
  this.eventType = 0;
  return "";
}

getLinkState (args, util){
  const linkID = args.linkID;

  return "";
}

sendPacketGlobal (args, util){
  const packetData = args.packetData;
  const linkID = args.linkID;
  const streamType = args.streamType;

  return "";
}

refreshUserlist (args, util){
  const linkID = args.linkID;

  return "";
}

disconnectFromLink (args, util){
  const linkID = args.linkID;
  
  return "";
}

disconnectAllLinks (args, util){
  
  return "";
}

}

Scratch.extensions.register(new cloudlink());
console.log("CloudLink API v" + vers + " | Ready!");
console.log("CloudLink API v" + vers + " | WARNING! You are using a BETA release of the CloudLink API Client! It may be unstable or buggy. YOU HAVE BEEN WARNED...");
