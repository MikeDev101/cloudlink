// MikeDEV's CloudLink API - Built upon KingdomPi's Scratch-websockets repo.
// See https://github.com/KingdomPy/scratch_websockets/blob/master/index.js for the original script!
// DO NOT USE ON OLDER WEB BROWSERS! CloudLink is designed to run best on a modern web browser.

const vers = 'S1.1';
const defIP = "wss://026b92bcc7b7.ngrok.io/";

var myName = "";
var gotNewGlobalData = false;
var gotNewPrivateData = false;
var sGData = "";
var sPData = "";
var isRunning = false;
var sys_status = 0;
var userNames = "";

class cloudlink {
	constructor(runtime, extensionId) {
		this.runtime = runtime;
	}
	static get STATE_KEY() {
		return 'Scratch.websockets';
	}
	getInfo() {
		return {
			id: 'cloudlink',
			name: 'CloudLink',
			color1: '#054c63',
			color2: '#054c63',
			color3: '#043444',
			blockIconURI: 'data:image/svg+xml;base64,PHN2ZyB2ZXJzaW9uPSIxLjEiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgeG1sbnM6eGxpbms9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkveGxpbmsiIHdpZHRoPSI2OS43NjY3MSIgaGVpZ2h0PSI1MS41Mzk5NCIgdmlld0JveD0iMCwwLDY5Ljc2NjcxLDUxLjUzOTk0Ij48ZyB0cmFuc2Zvcm09InRyYW5zbGF0ZSgtMjA1LjExNjY1LC0xNTQuMjMwMDMpIj48ZyBkYXRhLXBhcGVyLWRhdGE9InsmcXVvdDtpc1BhaW50aW5nTGF5ZXImcXVvdDs6dHJ1ZX0iIGZpbGwtcnVsZT0ibm9uemVybyIgc3Ryb2tlPSIjZmZmZmZmIiBzdHJva2Utd2lkdGg9IjQiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIgc3Ryb2tlLW1pdGVybGltaXQ9IjEwIiBzdHJva2UtZGFzaGFycmF5PSIiIHN0cm9rZS1kYXNob2Zmc2V0PSIwIiBzdHlsZT0ibWl4LWJsZW5kLW1vZGU6IG5vcm1hbCI+PHBhdGggZD0iTTI3Mi44ODMzNiwxODguODA3NTJjMCw4LjI2MzUzIC02LjY5ODkxLDE0Ljk2MjQ0IC0xNC45NjI0NCwxNC45NjI0NGgtMjYuOTMyMzljLTEyLjQ0MzE3LDAuMDA5MjggLTIyLjgxODksLTkuNTE1NDggLTIzLjg3MTg4LC0yMS45MTQwM2MtMS4wNTI5OCwtMTIuMzk4NTUgNy41Njc5MywtMjMuNTM2NjUgMTkuODM0NDUsLTI1LjYyNTljMTIuMjY2NTIsLTIuMDg5MjUgMjQuMDg4NDksNS41NjcgMjcuMTk5MjksMTcuNjE1MDVoMy43NzA1M2M4LjI2MzUzLDAgMTQuOTYyNDQsNi42OTg5MSAxNC45NjI0NCwxNC45NjI0NHoiIGRhdGEtcGFwZXItZGF0YT0ieyZxdW90O29yaWdQb3MmcXVvdDs6bnVsbH0iIGZpbGw9IiMwNTRjNjMiLz48ZyBkYXRhLXBhcGVyLWRhdGE9InsmcXVvdDtvcmlnUG9zJnF1b3Q7Om51bGx9IiBmaWxsPSJub25lIj48cGF0aCBkPSJNMjIxLjcxODI0LDE4MC44NjkxN2M1LjY2NjIxLC00LjcxOTU0IDEzLjg5NDUzLC00LjcxOTU0IDE5LjU2MDc0LDAiLz48cGF0aCBkPSJNMjE2Ljc0NDcsMTc1LjkzNzMxYzguNDAwMTEsLTcuNDA0NDYgMjAuOTk2NTYsLTcuNDA0NDYgMjkuMzk2NjgsMCIvPjxwYXRoIGQ9Ik0yMjYuNjIyMzIsMTg1LjgxNDkzYzIuODkwODEsLTIuMDUzNzggNi43NjQ1MywtMi4wNTM3OCA5LjY1NTM0LDAiLz48cGF0aCBkPSJNMjMxLjQ1NjkzLDE5MS4yMTkxNGgtMC4wMTM4OSIvPjwvZz48L2c+PC9nPjwvc3ZnPg==',
			menuIconURI: 'data:image/svg+xml;base64,PHN2ZyB2ZXJzaW9uPSIxLjEiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgeG1sbnM6eGxpbms9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkveGxpbmsiIHdpZHRoPSI0OC45OTk3NSIgaGVpZ2h0PSI0OC45OTk3NSIgdmlld0JveD0iMCwwLDQ4Ljk5OTc1LDQ4Ljk5OTc1Ij48ZyB0cmFuc2Zvcm09InRyYW5zbGF0ZSgtMjE1LjUwMDEyLC0xNTUuNTAwMTIpIj48ZyBkYXRhLXBhcGVyLWRhdGE9InsmcXVvdDtpc1BhaW50aW5nTGF5ZXImcXVvdDs6dHJ1ZX0iIGZpbGwtcnVsZT0ibm9uemVybyIgc3Ryb2tlPSIjZmZmZmZmIiBzdHJva2Utd2lkdGg9IjQiIHN0cm9rZS1taXRlcmxpbWl0PSIxMCIgc3Ryb2tlLWRhc2hhcnJheT0iIiBzdHJva2UtZGFzaG9mZnNldD0iMCIgc3R5bGU9Im1peC1ibGVuZC1tb2RlOiBub3JtYWwiPjxwYXRoIGQ9Ik0yMTcuNTAwMTMsMTgwYzAsLTEyLjQyNjM0IDEwLjA3MzUzLC0yMi40OTk4OCAyMi40OTk4OCwtMjIuNDk5ODhjMTIuNDI2MzQsMCAyMi40OTk4NywxMC4wNzM1MyAyMi40OTk4NywyMi40OTk4OGMwLDEyLjQyNjM0IC0xMC4wNzM1MywyMi40OTk4OCAtMjIuNDk5ODcsMjIuNDk5ODhjLTEyLjQyNjM0LDAgLTIyLjQ5OTg4LC0xMC4wNzM1MyAtMjIuNDk5ODgsLTIyLjQ5OTg4eiIgZGF0YS1wYXBlci1kYXRhPSJ7JnF1b3Q7b3JpZ1BvcyZxdW90OzpudWxsfSIgZmlsbD0iIzA1NGM2MyIgc3Ryb2tlLWxpbmVjYXA9ImJ1dHQiIHN0cm9rZS1saW5lam9pbj0ibWl0ZXIiLz48ZyBkYXRhLXBhcGVyLWRhdGE9InsmcXVvdDtvcmlnUG9zJnF1b3Q7Om51bGx9IiBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwYXRoIGQ9Ik0yMzAuMjc1MiwxODAuMDY3NjJjNS42NjYyMSwtNC43MTk1NCAxMy44OTQ1MywtNC43MTk1NCAxOS41NjA3NCwwIi8+PHBhdGggZD0iTTIyNS4zMDE2NiwxNzUuMTM1NzZjOC40MDAxMSwtNy40MDQ0NiAyMC45OTY1NiwtNy40MDQ0NiAyOS4zOTY2OCwwIi8+PHBhdGggZD0iTTIzNS4xNzkyOCwxODUuMDEzMzhjMi44OTA4MSwtMi4wNTM3OCA2Ljc2NDUzLC0yLjA1Mzc4IDkuNjU1MzQsMCIvPjxwYXRoIGQ9Ik0yNDAuMDEzODksMTkwLjQxNzU5aC0wLjAxMzg5Ii8+PC9nPjwvZz48L2c+PC9zdmc+',
			blocks: [{
				opcode: 'getVersion',
				blockType: Scratch.BlockType.REPORTER,
				text: 'Version',
			},{
				opcode: 'getGData',
				blockType: Scratch.BlockType.REPORTER,
				text: 'Socket Data (Global)',
			}, {
				opcode: 'getPData',
				blockType: Scratch.BlockType.REPORTER,
				text: 'Socket Data (Private)',
			}, {
				opcode: 'getStatus',
				blockType: Scratch.BlockType.REPORTER,
				text: 'Status',
			}, {
				opcode: 'getCNames',
				blockType: Scratch.BlockType.REPORTER,
				text: 'Connected Users',
			}, {
				opcode: 'getMyName',
				blockType: Scratch.BlockType.REPORTER,
				text: 'My Username',
			}, {
				opcode: 'getSocketState',
				blockType: Scratch.BlockType.BOOLEAN,
				text: 'Connected?',
			}, {
				opcode: 'isNewGlobalData',
				blockType: Scratch.BlockType.BOOLEAN,
				text: 'Got New Data (Global)?',
			}, {
				opcode: 'isNewPrivateData',
				blockType: Scratch.BlockType.BOOLEAN,
				text: 'Got New Data (Private)?',
			}, {
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
			}, {
				opcode: 'openSocket',
				blockType: Scratch.BlockType.COMMAND,
				text: 'Connect to [WSS]',
				arguments: {
					WSS: {
						type: Scratch.ArgumentType.STRING,
						defaultValue: defIP,
					},
				},
			}, {
				opcode: 'closeSocket',
				blockType: Scratch.BlockType.COMMAND,
				text: 'Disconnect',
			}, {
				opcode: 'sendGData',
				blockType: Scratch.BlockType.COMMAND,
				text: 'Send [DATA] (Global)',
				arguments: {
					DATA: {
						type: Scratch.ArgumentType.STRING,
						defaultValue: 'thing',
					},
				},
			}, {
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
			}, {
				opcode: 'setMyName',
				blockType: Scratch.BlockType.COMMAND,
				text: 'Set [NAME] as my username',
				arguments: {
					NAME: {
						type: Scratch.ArgumentType.STRING,
						defaultValue: 'a name',
					},
				},
			}, {
				opcode: 'resetGotNewGlobalData',
				blockType: Scratch.BlockType.COMMAND,
				text: 'Reset Got New Data (Global)',
			}, {
				opcode: 'resetGotNewPrivateData',
				blockType: Scratch.BlockType.COMMAND,
				text: 'Reset Got New Data (Private)',
			}, {
				opcode: 'refreshUserList',
				blockType: Scratch.BlockType.COMMAND,
				text: 'Refresh User List',
			}, ],
		};
	}
	openSocket(args) {
		const WSS = args.WSS; // Begin the main updater scripts
		if (isRunning == false) {
			const self = this;
			sys_status = 1;
			console.log("Establishing connection...");
			this.wss = new WebSocket(WSS);
			this.wss.onopen = function(e) {
				isRunning = true;
				sys_status = 2; // Connected OK value
				console.log("Connected.");
			};
			this.wss.onmessage = function(event) {
				var obj = JSON.parse(event.data);
				if (obj["type"] == "gs") {
					sGData = String(obj["data"]);
					gotNewGlobalData = true;
				} else if (obj["type"] == "ps") {
					if (String(obj["id"]) == String(myName)) {
						sPData = String(obj["data"]);
						gotNewPrivateData = true;
					};
				} else if (obj["type"] == "ul") {
					userNames = String(obj["data"]);
				} else if (obj["type"] == "ru") {
					if (myName != "") {
						self.wss.send("<%sn>\n" + myName)
					}
				} else {
					console.log("Error! Unknown command: " + String(obj));
				};
			};
			this.wss.onclose = function(event) {
				userNames = "";
				sGData = "";
				sPData = "";
				isRunning = false;
				gotNewGlobalData = false;
				gotNewPrivateData = false;
				myName = "";
				if (event.wasClean) {
					sys_status = 3; // Disconnected OK value
					console.log("Disconnected.");
				} else {
					sys_status = 4; // Connection lost value
					console.log("Lost connection to the server.");
				};
			};
		} else {
			return ("Connection already established.");
		};
	} // end the updater scripts
	closeSocket() {
		const self = this;
		if (isRunning == true) {
			this.wss.send("<%ds>\n" + myName); // send disconnect command in header before shutting down link
			this.wss.close(1000);
			isRunning = false;
			myName = "";
			gotNewGlobalData = false;
			gotNewPrivateData = false;
			userNames = "";
			sGData = "";
			sPData = "";
			sys_status = 3; // Disconnected OK value
			return ("Connection closed.");
		} else {
			return ("Connection already closed.");
		};
	}
	getSocketState() {
		return isRunning;
	}
	sendGData(args) {
		if (isRunning == true) {
			this.wss.send("<%gs>\n" + myName + "\n" + args.DATA); // begin packet data with global stream idenifier in the header
			return "Sent data successfully.";
		} else {
			return "Connection closed, no action taken.";
		}
	}
	sendPData(args) {
		if (myName != "") {
			if (isRunning == true) {
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
		return sGData;
	}
	getPData() {
		return sPData;
	}
	getStatus() {
		return sys_status;
	}
	getCNames() {
		return userNames;
	}
	getMyName() {
		return myName;
	}
	setMyName(args) {
		if (myName == "") {
			if (isRunning == true) {
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
		if (gotNewGlobalData == true) {
			gotNewGlobalData = false;
		};
	}
	resetGotNewPrivateData() {
		if (gotNewPrivateData == true) {
			gotNewPrivateData = false;
		};
	}
	refreshUserList() {
		if (isRunning == true) {
			this.wss.send("<%rf>\n"); // begin packet data with global stream idenifier in the header
			return "Sent request successfully.";
		} else {
			return "Connection closed, no action taken.";
		}
	}
	getVersion() {
		return vers
	}
}

Scratch.extensions.register(new cloudlink());
console.log("MikeDEV Says: Hello! I've successfully loaded CloudLink v"+ vers + ", have fun!");
