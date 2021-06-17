const vers = 'B3.0'; // Suite version number
const defIP = "ws://127.0.0.1:3000/"; // Default IP address
const testIP = ""; // Public test server IP.

// CloudLink icons
const cl_icon = 'data:image/svg+xml;base64,PHN2ZyB2ZXJzaW9uPSIxLjEiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgeG1sbnM6eGxpbms9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkveGxpbmsiIHdpZHRoPSI0NC45OTk3NSIgaGVpZ2h0PSI0NC45OTk3NiIgdmlld0JveD0iMCwwLDQ0Ljk5OTc1LDQ0Ljk5OTc2Ij48ZyB0cmFuc2Zvcm09InRyYW5zbGF0ZSgtMjE3LjUwMDE0LC0xNTcuNTAwMTMpIj48ZyBkYXRhLXBhcGVyLWRhdGE9InsmcXVvdDtpc1BhaW50aW5nTGF5ZXImcXVvdDs6dHJ1ZX0iIGZpbGwtcnVsZT0ibm9uemVybyIgc3Ryb2tlPSIjZmZmZmZmIiBzdHJva2UtbWl0ZXJsaW1pdD0iMTAiIHN0cm9rZS1kYXNoYXJyYXk9IiIgc3Ryb2tlLWRhc2hvZmZzZXQ9IjAiIHN0eWxlPSJtaXgtYmxlbmQtbW9kZTogbm9ybWFsIj48cGF0aCBkPSJNMjE3LjUwMDE0LDE4MC4wMDAwMWMwLC0xMi40MjYzNCAxMC4wNzM1MywtMjIuNDk5ODggMjIuNDk5ODgsLTIyLjQ5OTg4YzEyLjQyNjM0LDAgMjIuNDk5ODcsMTAuMDczNTMgMjIuNDk5ODcsMjIuNDk5ODhjMCwxMi40MjYzNCAtMTAuMDczNTMsMjIuNDk5ODggLTIyLjQ5OTg3LDIyLjQ5OTg4Yy0xMi40MjYzNCwwIC0yMi40OTk4OCwtMTAuMDczNTMgLTIyLjQ5OTg4LC0yMi40OTk4OHoiIGRhdGEtcGFwZXItZGF0YT0ieyZxdW90O29yaWdQb3MmcXVvdDs6bnVsbH0iIGZpbGw9IiMwZTlhNmMiIHN0cm9rZS13aWR0aD0iMCIgc3Ryb2tlLWxpbmVjYXA9ImJ1dHQiIHN0cm9rZS1saW5lam9pbj0ibWl0ZXIiLz48ZyBkYXRhLXBhcGVyLWRhdGE9InsmcXVvdDtvcmlnUG9zJnF1b3Q7Om51bGx9IiBmaWxsPSJub25lIiBzdHJva2Utd2lkdGg9IjQiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PHBhdGggZD0iTTIzMC4yNzUyMSwxODAuMDY3NjNjNS42NjYyMSwtNC43MTk1NCAxMy44OTQ1MywtNC43MTk1NCAxOS41NjA3NCwwIi8+PHBhdGggZD0iTTIyNS4zMDE2NywxNzUuMTM1NzdjOC40MDAxMSwtNy40MDQ0NiAyMC45OTY1NiwtNy40MDQ0NiAyOS4zOTY2OCwwIi8+PHBhdGggZD0iTTIzNS4xNzkyOSwxODUuMDEzMzljMi44OTA4MSwtMi4wNTM3OCA2Ljc2NDUzLC0yLjA1Mzc4IDkuNjU1MzQsMCIvPjxwYXRoIGQ9Ik0yNDAuMDEzOSwxOTAuNDE3NmgtMC4wMTM4OSIvPjwvZz48L2c+PC9nPjwvc3ZnPg==';
const cl_block = 'data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0idXRmLTgiPz4NCjwhLS0gR2VuZXJhdG9yOiBBZG9iZSBJbGx1c3RyYXRvciAyNS4yLjMsIFNWRyBFeHBvcnQgUGx1Zy1JbiAuIFNWRyBWZXJzaW9uOiA2LjAwIEJ1aWxkIDApICAtLT4NCjxzdmcgdmVyc2lvbj0iMS4xIiBpZD0iTGF5ZXJfMSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiB4bWxuczp4bGluaz0iaHR0cDovL3d3dy53My5vcmcvMTk5OS94bGluayIgeD0iMHB4IiB5PSIwcHgiDQoJIHZpZXdCb3g9IjAgMCA0NSA0NSIgc3R5bGU9ImVuYWJsZS1iYWNrZ3JvdW5kOm5ldyAwIDAgNDUgNDU7IiB4bWw6c3BhY2U9InByZXNlcnZlIj4NCjxzdHlsZSB0eXBlPSJ0ZXh0L2NzcyI+DQoJLnN0MHtmaWxsOiMwRkJEOEM7fQ0KCS5zdDF7ZmlsbDpub25lO3N0cm9rZTojRkZGRkZGO3N0cm9rZS13aWR0aDo0O3N0cm9rZS1saW5lY2FwOnJvdW5kO3N0cm9rZS1saW5lam9pbjpyb3VuZDtzdHJva2UtbWl0ZXJsaW1pdDoxMDt9DQo8L3N0eWxlPg0KPGcgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoLTIxNy41MDAxNCwtMTU3LjUwMDEzKSI+DQoJPGc+DQoJCTxwYXRoIGNsYXNzPSJzdDAiIGQ9Ik0yMTcuNSwxODBjMC0xMi40LDEwLjEtMjIuNSwyMi41LTIyLjVzMjIuNSwxMC4xLDIyLjUsMjIuNXMtMTAuMSwyMi41LTIyLjUsMjIuNVMyMTcuNSwxOTIuNCwyMTcuNSwxODANCgkJCUwyMTcuNSwxODB6Ii8+DQoJCTxnPg0KCQkJPHBhdGggY2xhc3M9InN0MSIgZD0iTTIzMC4zLDE4MC4xYzUuNy00LjcsMTMuOS00LjcsMTkuNiwwIi8+DQoJCQk8cGF0aCBjbGFzcz0ic3QxIiBkPSJNMjI1LjMsMTc1LjFjOC40LTcuNCwyMS03LjQsMjkuNCwwIi8+DQoJCQk8cGF0aCBjbGFzcz0ic3QxIiBkPSJNMjM1LjIsMTg1YzIuOS0yLjEsNi44LTIuMSw5LjcsMCIvPg0KCQkJPHBhdGggY2xhc3M9InN0MSIgZD0iTTI0MCwxOTAuNEwyNDAsMTkwLjQiLz4NCgkJPC9nPg0KCTwvZz4NCjwvZz4NCjwvc3ZnPg0K';

// Booleans for signifying an update to the global or private data streams, as well as the disk and coin data.
var gotNewGlobalData = false; 
var gotNewPrivateData = false;

// Variables storing global and private stream data transmitted from the server.
var sGData = "";
var sPData = "";

// System variables needed for basic functionality
var sys_status = 0; // System status reporter, 0 = Ready, 1 = Connecting, 2 = Connected, 3 = Disconnected OK, 4 = Disconnected ERR
var userNames = ""; // Usernames list
var uList = "";
var myName = ""; // Username reporter
var servIP = defIP; // Default server IP
var isRunning = false; // Boolean for determining if the connection is alive and well
var wss = null; // Websocket object that enables communications
var serverVersion = ''; // Diagnostics, gets the server's value for 'vers'.
var globalVars = {}; // Custom globally-readable variables.
var privateVars = {}; // Custom private variables.
var gotNewGlobalVarData = {}; // Booleans for checking if a new value has been written to a global var.
var gotNewPrivateVarData = {}; // Booleans for checking if a new value has been written to a private var.

// CloudLink class for the primary extension.
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
			color1: '#0FBD8C',
			color2: '#0FBD8C',
			color3: '#0FBD8C',
			blockIconURI: cl_block,
			menuIconURI: cl_icon,
			blocks: [
			{
				opcode: 'returnGlobalData',
				blockType: Scratch.BlockType.REPORTER,
				text: 'Global data',
			}, 	{
				opcode: 'returnPrivateData',
				blockType: Scratch.BlockType.REPORTER,
				text: 'Private data',
			}, 	{
				opcode: 'returnLinkData',
				blockType: Scratch.BlockType.REPORTER,
				text: 'Link Status',
			}, 	{
				opcode: 'returnUserListData',
				blockType: Scratch.BlockType.REPORTER,
				text: 'Usernames',
			}, 	{
				opcode: 'returnUsernameData',
				blockType: Scratch.BlockType.REPORTER,
				text: 'My Username',
			}, 	{
				opcode: 'returnVersionData',
				blockType: Scratch.BlockType.REPORTER,
				text: 'Extension Version',
			}, 	{
				opcode: 'returnServerVersion',
				blockType: Scratch.BlockType.REPORTER,
				text: 'Server Version',
			}, {
				opcode: 'returnTestIPData',
				blockType: Scratch.BlockType.REPORTER,
				text: 'Test IP',
			}, 	{
				opcode: 'returnVarData',
				blockType: Scratch.BlockType.REPORTER,
				text: '[TYPE] var [VAR] data',
				arguments: {
					VAR: {
						type: Scratch.ArgumentType.STRING,
						defaultValue: 'Apple',
					},
					TYPE: {
						type: Scratch.ArgumentType.STRING,
						menu: 'varmenu',
						defaultValue: 'Global',
					},
				},
			},	{
				opcode: 'parseJSON',
				blockType: Scratch.BlockType.REPORTER,
				text: '[PATH] of [JSON_STRING]',
				arguments: {
					PATH: {
						type: Scratch.ArgumentType.STRING,
						defaultValue: 'fruit/apples',
					},
					JSON_STRING: {
						type: Scratch.ArgumentType.STRING,
						defaultValue: '{"fruit": {"apples": 2, "bananas": 3}, "total_fruit": 5}',
					},
				},
			}, 	{
				opcode: 'getComState',
				blockType: Scratch.BlockType.BOOLEAN,
				text: 'Connected?',
			}, 	{
				opcode: 'getUsernameState',
				blockType: Scratch.BlockType.BOOLEAN,
				text: 'Username synced?',
			}, 	{
				opcode: 'returnIsNewData',
				blockType: Scratch.BlockType.BOOLEAN,
				text: 'Got New [TYPE] Data?',
				arguments: {
					TYPE: {
						type: Scratch.ArgumentType.STRING,
						menu: 'datamenu',
						defaultValue: 'Global',
					},
				},
			}, 	{
				opcode: 'returnIsNewVarData',
				blockType: Scratch.BlockType.BOOLEAN,
				text: 'Got New [TYPE] Var [VAR] Data?',
				arguments: {
					VAR: {
						type: Scratch.ArgumentType.STRING,
						defaultValue: 'Apple',
					},
					TYPE: {
						type: Scratch.ArgumentType.STRING,
						menu: 'varmenu',
						defaultValue: 'Global',
					},
				},
			}, {
				opcode: 'checkForID',
				blockType: Scratch.BlockType.BOOLEAN,
				text: 'ID [ID] Connected?',
				arguments: {
					ID: {
						type: Scratch.ArgumentType.STRING,
						defaultValue: 'Another name',
					},
				},
			}, {
				opcode: 'openSocket',
				blockType: Scratch.BlockType.COMMAND,
				text: 'Connect to [IP]',
				arguments: {
					IP: {
						type: Scratch.ArgumentType.STRING,
						defaultValue: defIP,
					},
				},
			}, 	{
				opcode: 'closeSocket',
				blockType: Scratch.BlockType.COMMAND,
				text: 'Disconnect',
			}, 	{
				opcode: 'setMyName',
				blockType: Scratch.BlockType.COMMAND,
				text: 'Set [NAME] as username',
				arguments: {
					NAME: {
						type: Scratch.ArgumentType.STRING,
						defaultValue: 'A name',
					},
				},
			},	{
				opcode: 'sendGData',
				blockType: Scratch.BlockType.COMMAND,
				text: 'Send [DATA]',
				arguments: {
					DATA: {
						type: Scratch.ArgumentType.STRING,
						defaultValue: 'Apple',
					},
				},
			}, 	{
				opcode: 'sendPData',
				blockType: Scratch.BlockType.COMMAND,
				text: 'Send [DATA] to [ID]',
				arguments: {
					DATA: {
						type: Scratch.ArgumentType.STRING,
						defaultValue: 'Apple',
					},
					ID: {
						type: Scratch.ArgumentType.STRING,
						defaultValue: 'A name',
					},
				},
			},  {
				opcode: 'sendGDataAsVar',
				blockType: Scratch.BlockType.COMMAND,
				text: 'Send Var [VAR] with Data [DATA]',
				arguments: {
					DATA: {
						type: Scratch.ArgumentType.STRING,
						defaultValue: 'Banana',
					},
					VAR: {
						type: Scratch.ArgumentType.STRING,
						defaultValue: 'Apple',
					},
				},
			},	{
				opcode: 'sendPDataAsVar',
				blockType: Scratch.BlockType.COMMAND,
				text: 'Send Var [VAR] to [ID] with Data [DATA]',
				arguments: {
					DATA: {
						type: Scratch.ArgumentType.STRING,
						defaultValue: 'Banana',
					},
					ID: {
						type: Scratch.ArgumentType.STRING,
						defaultValue: 'A name',
					},
					VAR: {
						type: Scratch.ArgumentType.STRING,
						defaultValue: 'Apple',
					},
				},
			},	{
				opcode: 'resetNewData',
				blockType: Scratch.BlockType.COMMAND,
				text: 'Reset Got New [TYPE] Data',
				arguments: {
					TYPE: {
						type: Scratch.ArgumentType.STRING,
						menu: 'datamenu',
						defaultValue: 'Global',
					},
				},
			},	{
				opcode: 'resetNewVarData',
				blockType: Scratch.BlockType.COMMAND,
				text: 'Reset Got New [TYPE] Var [VAR] Data',
				arguments: {
					TYPE: {
						type: Scratch.ArgumentType.STRING,
						menu: 'varmenu',
						defaultValue: 'Global',
					},
					VAR: {
						type: Scratch.ArgumentType.STRING,
						defaultValue: 'Apple',
					},
				},
			},
			],
			menus: {
				coms: {
					items: ["Connected", "Username Synced"]
				},
				datamenu: {
					items: ['Global', 'Private', 'Global (Linked)', 'Private (Linked)'],
				},
				varmenu: {
					items: ['Global', 'Private'],
				},
			}
		};
	}; 
	openSocket(args) {
		servIP = args.IP; // Begin the main updater scripts
		if (!isRunning) {
			sys_status = 1;
			console.log("Establishing connection");
			try {
				wss = new WebSocket(servIP);
				wss.onopen = function(e) {
					isRunning = true;
					sys_status = 2; // Connected OK value
					console.log("Connected");
				};
				wss.onmessage = function(event) {
					var rawpacket = String(event.data);
					var obj = JSON.parse(rawpacket);
					
					// console.log("Got new packet");
					// console.log(obj);
					
					// Global Messages
					if (obj["cmd"] == "gmsg") {
						sGData = String(obj["val"]);
						gotNewGlobalData = true;
					};
					// Private Messages
					if (obj["cmd"] == "pmsg") {
						sPData = String(obj["val"]);
						gotNewPrivateData = true;
					};
					// Username List
					if (obj["cmd"] == "ulist") {
						userNames = String(obj["val"]);
						userNames = userNames.split(";");
						userNames.pop();
						var uListTemp = "";
						var i;
						for (i = 0; i < userNames.length; i++) {
							if (!userNames[i].includes("%")) {
								uListTemp = (String(uListTemp) + String(userNames[i])+ "; ");
							};
						};
						uList = uListTemp;
					};
					// Direct COMS (Fetches server metadata)
					if (obj["cmd"] == "direct") {
						var ddata = obj['data'];
						if (ddata['cmd'] == "vers") {
							serverVersion = ddata["data"];
							console.log("Server version: " + String(serverVersion));
						};
					};
					// Global Variables
					if (obj["cmd"] == "gvar") {
						globalVars[obj["name"]] = obj["val"];
						gotNewGlobalVarData[obj["name"]] = true;
					};
					// Private Variables
					if (obj["cmd"] == "pvar") {
						privateVars[obj["name"]] = obj["val"];
						gotNewPrivateVarData[obj["name"]] = true;
					};
					// Server soft-shutdown handler
					if (obj["cmd"] == "ds") {
						console.log("Server is shutting down, disconnecting");
						wss.close(1000);
					};
					
				};
				wss.onclose = function(event) {
					isRunning = false;
					myName = "";
					gotNewGlobalData = false;
					gotNewPrivateData = false;
					userNames = "";
					sGData = "";
					sPData = "";
					sys_status = 3; // Disconnected OK value
					serverVersion = '';
					globalVars = {};
					privateVars = {};
					gotNewGlobalVarData = {};
					gotNewPrivateVarData = {};
					uList = "";
					wss = null;
					sys_status = 3;
					console.log("Disconnected");
					};
			} catch(err) {
				throw(err)
			};
		};
	}; // end the updater scripts
	closeSocket() {
		if (isRunning) {
			wss.close(1000);
			isRunning = false;
			myName = "";
			gotNewGlobalData = false;
			gotNewPrivateData = false;
			userNames = "";
			sGData = "";
			sPData = "";
			sys_status = 3; // Disconnected OK value
			serverVersion = '';
			globalVars = {};
			privateVars = {};
			gotNewGlobalVarData = {};
			gotNewPrivateVarData = {};
			uList = "";
			wss = null;
		};
	};
	getComState() {
		return isRunning;
	};
	checkForID(args) {
		if (isRunning) {
			return (userNames.indexOf(String(args.ID)) >= 0);
		} else {
			return false;
		};
	};
	getUsernameState() {
		if (isRunning) {
			if (String(myName) != '') {
				return (userNames.indexOf(String(myName)) >= 0);
			} else {
				return false;
			}
		} else {
			return false;
		};
	};
	sendGData(args) {
		if (isRunning) {
			if (!(String(args.DATA).length > 1000)) {
				wss.send(JSON.stringify({
					cmd: "gmsg",
					val: args.DATA
				}));
			} else {
				console.log("Blocking attempt to send packet larger than 1000 bytes (1 KB), packet is " + String(String(args.DATA).length) + " bytes");
			};
		};
	};
	sendPData(args) {
		if (isRunning) {
			if (String(myName) != "") {
				if (userNames.indexOf(String(args.ID)) >= 0) {
					if (!(String(args.DATA).length > 1000)) {
						wss.send(JSON.stringify({
						cmd: "pmsg",
						id: args.ID,
						val: args.DATA
						}));
					} else {
						console.log("Blocking attempt to send packet larger than 1000 bytes (1 KB), packet is " + String(String(args.DATA).length) + " bytes");
					};
				} else {
					console.log("Blocking attempt to send private packet to nonexistent ID");
				};
			};
		};
	}; 
	sendGDataAsVar(args) {
		if (isRunning) {
			if (!(String(args.DATA).length > 1000)) {
				wss.send(JSON.stringify({
					cmd: "gvar",
					name: args.VAR,
					val: args.DATA
				}));
			} else {
				console.log("Blocking attempt to send packet larger than 1000 bytes (1 KB), packet is " + String(String(args.DATA).length) + " bytes");
			};
		};
	};
	sendPDataAsVar(args) {
		if (isRunning) {
			if (String(myName) != "") {
				if (userNames.indexOf(String(args.ID)) >= 0) {
					if (!(String(args.DATA).length > 1000)) {
						wss.send(JSON.stringify({
							cmd: "pvar",
							name: args.VAR,
							id: args.ID,
							val: args.DATA
						}));
					} else {
						console.log("Blocking attempt to send packet larger than 1000 bytes (1 KB), packet is " + String(String(args.DATA).length) + " bytes");
					};	
				} else {
					console.log("Blocking attempt to send private variable packet to nonexistent ID");
				};
			};
		};
	};
	returnGlobalData() {
		return sGData;
	};
	returnPrivateData() {
		return sPData;
	};
	returnGlobalLinkedData() {
		return sGLinkedData;
	};
	returnPrivateLinkedData() {
		return sPLinkedData;
	};
	returnVarData(args) {
		if (args.TYPE == "Global") {
			if (args.VAR in globalVars) {
				return globalVars[args.VAR];
			} else {
				return "";
			}
		} else if (args.TYPE == "Private") {
			if (args.VAR in privateVars) {
				return privateVars[args.VAR];
			} else {
				return "";
			}
		}
	};
	returnIsNewVarData(args) {
		if (args.TYPE == "Global") {
			if (args.VAR in globalVars) {
				return gotNewGlobalVarData[args.VAR];
			} else {
				return false;
			}
		} else if (args.TYPE == "Private") {
			if (args.VAR in privateVars) {
				return gotNewPrivateVarData[args.VAR];
			} else {
				return false;
			}
		};
	};
	returnLinkData() {
		return sys_status;
	}; 
	returnUserListData() {
		return uList;
	}; 
	returnUsernameData() {
		return myName;
	}; 
	returnVersionData() {
		return vers;
	}; 
	returnTestIPData() {
		return testIP;
	};
	returnServerVersion() {
		return serverVersion;
	};
	returnIsNewData(args) {
		if (args.TYPE == "Global") {
			return gotNewGlobalData;
		};
		if (args.TYPE == "Private") {
			return gotNewPrivateData;
		};
		if (args.TYPE == "Global (Linked)") {
			return gotNewGlobalLinkedData;
		};
		if (args.TYPE == "Private (Linked)") {
			return gotNewPrivateLinkedData;
		};
	}
	setMyName(args) {
		if (isRunning) {
			if (myName == ""){
				if (String(args.NAME) != "") {
					if (!(userNames.indexOf(args.NAME) >= 0)) {
						if ((!(String(args.NAME).length > 20))) {
							if (!(args.NAME == "%CA%" || args.NAME == "%CC%" || args.NAME == "%CD%" || args.NAME == "%MS%")){
								wss.send(JSON.stringify({
									cmd: "setid",
									val: String(args.NAME)
								}));
								myName = args.NAME;
							} else {
								console.log("Blocking attempt to use reserved usernames");
							};
						} else {
							console.log("Blocking attempt to use username larger than 20 characters, username is " + String(String(args.NAME).length) + " characters long");
						};
					} else {
						console.log("Blocking attempt to use duplicate username");
					};
				} else {
					console.log("Blocking attempt to use blank username");
				};
			} else {
				console.log("Username already has been set");
			};
		};
	};
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
	};
	resetNewData(args) {
		if (args.TYPE == "Global") {
			if (gotNewGlobalData == true) {
				gotNewGlobalData = false;
			};
		};
		if (args.TYPE == "Private") {
			if (gotNewPrivateData == true) {
				gotNewPrivateData = false;
			};
		};
		if (args.TYPE == "Global (Linked)") {
			if (gotNewGlobalLinkedData == true) {
				gotNewGlobalLinkedData = false;
			};
		};
		if (args.TYPE == "Private (Linked)") {
			if (gotNewPrivateLinkedData == true) {
				gotNewPrivateLinkedData = false;
			};
		};
	};
	resetNewVarData(args) {
		if (args.TYPE == "Global") {
			if (args.VAR in globalVars) {
				gotNewGlobalVarData[args.VAR] = false;
			}
		} else if (args.TYPE == "Private") {
			if (args.VAR in privateVars) {
				gotNewPrivateVarData[args.VAR] = false;
			}
		}
	};
};


Scratch.extensions.register(new cloudlink());
