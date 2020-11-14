// MikeDEV's CloudLink API Suite
// This extension combines the CloudLink API, the CloudCoin API, and the CloudDisk API in an all-in-one solution.
// Original Source Code built upon KingdomPi's Scratch-websockets repo.
// See https://github.com/KingdomPy/scratch_websockets/blob/master/index.js for the original script!
// DO NOT USE ON OLDER WEB BROWSERS! CloudLink is designed to run best on a modern web browser.

const vers = 'B2.5';
console.log("[CloudLink] Loading 1/3: Initializing the extension...")

// Booleans for signifying an update to the global or private data streams, as well as the disk and coin data.
var gotNewGlobalData = false; 
var gotNewPrivateData = false;
var gotNewTrade = false;
var gotDiskData = false;
var gotCoinData = false;
var gotAccountData = false;

// Variables storing global and private stream data transmitted from the server.
var sGData = "";
var sPData = "";

// System variables needed for basic functionality
var isRunning = false;
var sys_status = 0;
var userNames = "";
var myName = "";

// Variables for storing CloudCoin data
var coinData = '';
var tradeReturn = '';

// Variables for storing CloudAccount data
var isAuth = false;
var accountData = "";
var accMode = "";

// Variables for storing CloudDisk data
var diskData = '';
var runningFtp = false;
var ftpData = '';

console.log("[CloudLink] Loading 2/3: Loading the extension...")
// CloudLink Extension + CloudCoin and CloudDisk API interface.
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
			blocks: [
			{
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
			}, {
				opcode: 'returnData',
				blockType: Scratch.BlockType.REPORTER,
				text: '[MENU]',
				arguments: {
					MENU: {
						type: Scratch.ArgumentType.STRING,
						menu: 'reportermenu',
						defaultValue: 'Global Data',
					},
				},
			}, {
				opcode: 'getComState',
				blockType: Scratch.BlockType.BOOLEAN,
				text: '[com]?',
				arguments: {
					com: {
						type: Scratch.ArgumentType.STRING,
						menu: 'coms',
						defaultValue: 'Connected',
					},
				},
			}, {
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
			}, {
				opcode: 'openSocket',
				blockType: Scratch.BlockType.COMMAND,
				text: 'Connect to [WSS]',
				arguments: {
					WSS: {
						type: Scratch.ArgumentType.STRING,
						defaultValue: 'ws://127.0.0.1:3000/',
					},
				},
			}, {
				opcode: 'closeSocket',
				blockType: Scratch.BlockType.COMMAND,
				text: 'Disconnect',
			}, {
				opcode: 'sendGData',
				blockType: Scratch.BlockType.COMMAND,
				text: 'Send [DATA]',
				arguments: {
					DATA: {
						type: Scratch.ArgumentType.STRING,
						defaultValue: 'thing',
					},
				},
			}, {
				opcode: 'sendPData',
				blockType: Scratch.BlockType.COMMAND,
				text: 'Send [DATA] to [ID]',
				arguments: {
					DATA: {
						type: Scratch.ArgumentType.STRING,
						defaultValue: 'thing',
					},
					ID: {
						type: Scratch.ArgumentType.STRING,
						defaultValue: 'A name',
					},
				},
			},  {
				opcode: 'setMyName',
				blockType: Scratch.BlockType.COMMAND,
				text: 'Set [NAME] as username',
				arguments: {
					NAME: {
						type: Scratch.ArgumentType.STRING,
						defaultValue: 'A name',
					},
				},
			}, {
				opcode: 'refreshUserList',
				blockType: Scratch.BlockType.COMMAND,
				text: 'Refresh User List',
			}, {
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
			}, {
				opcode: 'getFTPFileList',
				blockType: Scratch.BlockType.COMMAND,
				text: 'Get a List of Files for FTP',
			}, 
			{
				opcode: 'getFTPFileInfo',
				blockType: Scratch.BlockType.COMMAND,
				text: 'Get file [fname] info for FTP',
				arguments: {
					fname: {
						type: Scratch.ArgumentType.STRING,
						defaultValue: 'sample.txt',
					},
				},
			}, {
				opcode: 'initFTP',
				blockType: Scratch.BlockType.COMMAND,
				text: 'Download file [fname] from FTP',
				arguments: {
					fname: {
						type: Scratch.ArgumentType.STRING,
						defaultValue: 'sample.txt',
					},
				},
			}, {
				opcode: 'abortFTP',
				blockType: Scratch.BlockType.COMMAND,
				text: 'Abort FTP'
			}, {
				opcode: 'readData',
				blockType: Scratch.BlockType.COMMAND,
				text: 'Read data on slot [slot]',
				arguments: {
					slot: {
						type: Scratch.ArgumentType.NUMBER,
						menu: 'diskSlot',
					},
				},
			}, {
				opcode: 'writeData',
				blockType: Scratch.BlockType.COMMAND,
				text: 'Write data [data] to slot [slot]',
				arguments: {
					data: {
						type: Scratch.ArgumentType.STRING,
						defaultValue: 'abc123',
					},
					slot: {
						type: Scratch.ArgumentType.NUMBER,
						menu: 'diskSlot',
					},
				},
			}, {
				opcode: 'doAcc',
				blockType: Scratch.BlockType.COMMAND,
				text: '[ACCMODE] with password [pswd]',
				arguments: {
					ACCMODE: {
						type: Scratch.ArgumentType.STRING,
						menu: 'accmenu',
						defaultValue: 'Login',
					},
					pswd: {
						type: Scratch.ArgumentType.STRING,
						defaultValue: ' ',
					},
				},
			}, {
				opcode: 'logoutAcc',
				blockType: Scratch.BlockType.COMMAND,
				text: 'Logout of account',
			}, {
				opcode: 'checkAcc',
				blockType: Scratch.BlockType.COMMAND,
				text: 'Check Account',
			}, {
				opcode: 'checkBal',
				blockType: Scratch.BlockType.COMMAND,
				text: 'Check Balance',
			}, {
				opcode: 'setCoins',
				blockType: Scratch.BlockType.COMMAND,
				text: '[coinmode] [coins] coins',
				arguments: {
					coins: {
						type: Scratch.ArgumentType.NUMBER,
						defaultValue: '50',
					},
					coinmode: {
						type: Scratch.ArgumentType.STRING,
						defaultValue: 'Spend',
						menu: 'coinmenu',
					},
				},
			}, {
				opcode: 'tradeCoins',
				blockType: Scratch.BlockType.COMMAND,
				text: 'Trade [coins] coins with [user]',
				arguments: {
					coins: {
						type: Scratch.ArgumentType.NUMBER,
						defaultValue: '50',
					},
					user: {
						type: Scratch.ArgumentType.STRING,
						defaultValue: 'A name',
					},
				},
			},
			],
			menus: {
				diskSlot: {
					acceptReporters: true,
					items: ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
				},
				coms: {
					items: ["Connected", "Account API Connected", "Coin API Connected", "Disk API Connected", "Logged in","Username Synced"],
				},
				coinmenu: {
					items: ['Spend', 'Earn'],
				},
				coinreporter: {
					items: ['Spend', 'Earn', 'Trade'],
				},
				datamenu: {
					items: ['Global', 'Private', 'Account', 'Coin', 'Disk', 'Trade'],
				},
				reportermenu: {
					items: ['Global Data', 'Private Data', 'Account Data', 'Disk Data', 'FTP Data', 'Coin Data', 'Trade Return', 'Link Status', 'Usernames', 'My Username', 'Version'],
				},
				accmenu: {
					items: ['Login', 'Register'],
				},
			}
		};
	};
	// CLOUDLINK OPCODES
	openSocket(args) {
		const WSS = args.WSS; // Begin the main updater scripts
		if (!isRunning) {
			const self = this;
			sys_status = 1;
			console.log("[CloudLink] Establishing connection...");
			this.wss = new WebSocket(WSS);
			this.wss.onopen = function(e) {
				isRunning = true;
				sys_status = 2; // Connected OK value
				console.log("[CloudLink] Connected.");
			};
			this.wss.onmessage = function(event) {
				var rawpacket = String(event.data)
				var obj = JSON.parse(event.data);
				if (obj["type"] == "gs") {
					sGData = String(obj["data"]);
					gotNewGlobalData = true;
				} else if (obj["type"] == "ps") {
					if (String(obj["id"]) == String(myName)) {
						sPData = String(obj["data"]);
						gotNewPrivateData = true;
					};
				} else if (obj["type"] == "dd") {
					if (String(obj["id"]) == String(myName)) {
						diskData = String(obj["data"]);
						gotDiskData = true;
					};
				} else if (obj["type"] == "ftp") {
					if (String(obj["id"]) == String(myName)) {
						if (runningFtp) {
							if (String(obj['data']) != "<TX>") {
								ftpData = String(String(ftpData) + String(obj["data"]));
							} else {
								runningFtp = false;
							};
						};
					};
				} else if (obj["type"] == "ca") {
					if (String(obj["id"]) == String(myName)) {
						if (String(obj["data"]) == "OK") {
							if (accMode == "LI"){
								isAuth = true;
								accMode = ""
							} if (accMode == "LO") {
								isAuth = false;
								accMode = ""
							} else {
								accMode = ""
								accountData = String(obj["data"]);
								gotAccountData = true;
							};
						} else {
							accMode = ""
							accountData = String(obj["data"]);
							gotAccountData = true;
						};
					};
				} else if (obj["type"] == "cd") {
					if (String(obj["id"]) == String(myName)) {
						coinData = String(obj["data"]);
						gotCoinData = true;
					};
				} else if (obj["type"] == "ul") {
					userNames = String(obj["data"]);
				} else if (obj["type"] == "ru") {
					if (myName != "") {
						self.wss.send("<%sn>\n" + myName)
					}
				} else {
					console.log("[CloudLink] Error! Unknown packet data: " + String(rawpacket));
				};
			};
			this.wss.onclose = function(event) {
				userNames = "";
				sGData = "";
				sPData = "";
				diskData = "";
				isRunning = false;
				gotNewGlobalData = false;
				gotNewPrivateData = false;
				gotNewTrade = false;
				gotDiskData = false;
				gotCoinData = false;
				gotAccountData = false;
				myName = "";
				coinData = "";
				tradeReturn = "";
				accountData = "";
				accMode = "";
				isAuth = false;
				runningFtp = false;
				ftpData = '';
				if (event.wasClean) {
					sys_status = 3; // Disconnected OK value
					console.log("[CloudLink] Disconnected.");
				} else {
					sys_status = 4; // Connection lost value
					console.log("[CloudLink] Lost connection to the server.");
				};
			};
		} else {
			return ("Connection already established.");
		};
	}; // end the updater scripts
	closeSocket() {
		const self = this;
		if (isRunning) {
			this.wss.send("<%ds>\n" + myName); // send disconnect command in header before shutting down link
			this.wss.close(1000);
			isRunning = false;
			myName = "";
			gotNewGlobalData = false;
			gotNewPrivateData = false;
			gotNewTrade = false;
			gotDiskData = false;
			gotCoinData = false;
			gotAccountData = false;
			userNames = "";
			sGData = "";
			sPData = "";
			coinData = "";
			tradeReturn = "";
			diskData = "";
			accountData = "";
			accMode = "";
			isAuth = false;
			sys_status = 3; // Disconnected OK value
			runningFtp = false;
			ftpData = '';
			return ("Connection closed.");
		} else {
			return ("Connection already closed.");
		};
	};
	getComState(args) {
		if (args.com == "Connected") {
			return isRunning;
		} if (args.com == "Coin API Connected") {
			if (isRunning) {
				return (userNames.indexOf('%CC%') >= 0);
			} else {
				return false;
			};
		} if (args.com == "Disk API Connected") {
			if (isRunning) {
				return (userNames.indexOf('%CD%') >= 0);
			} else {
				return false;
			};
		} if (args.com == "Account API Connected") {
			if (isRunning) {
				return (userNames.indexOf('%CA%') >= 0);
			} else {
				return false;
			};
		} if (args.com == "Logged in") {
			if (isRunning) {
				return isAuth;
			} else {
				return false;
			};
		} if (args.com == "Username Synced") {
			if (isRunning) {
				if (myName != '') {
					return (userNames.indexOf(String(myName)) >= 0);
				} else {
					return false;
				}
			} else {
				return false;
			}
		} else {
			return false;
		};
	};
	sendGData(args) {
		if (isRunning) {
			this.wss.send("<%gs>\n" + myName + "\n" + args.DATA); // begin packet data with global stream idenifier in the header
			return "Sent data successfully.";
		} else {
			return "Connection closed, no action taken.";
		}
	};
	sendPData(args) {
		if (isRunning) {
			if (myName != "") {
				if (args.user != myName) {
					this.wss.send("<%ps>\n" + myName + "\n" + args.ID + "\n" + args.DATA); // begin packet data with global stream idenifier in the header
					return "Sent data successfully.";
				} else {
					return "Can't send data to yourself!";
				};
			} else {
				return "Username not set, no action taken.";
			}
		} else {
			return "Connection closed, no action taken.";
		};
	};
	returnData(args) {
		if (args.MENU == "Global Data") {
			return sGData;
		};
		if (args.MENU == "Private Data") {
			return sPData;
		};
		if (args.MENU == "Account Data") {
			return accountData;
		};
		if (args.MENU == "Coin Data") {
			return coinData;
		};
		if (args.MENU == "Disk Data") {
			return diskData;
		};
		if (args.MENU == "Link Status") {
			return sys_status;
		}; 
		if (args.MENU == "Usernames") {
			return userNames;
		}; 
		if (args.MENU == "My Username") {
			return myName;
		}; 
		if (args.MENU == "Version") {
			return vers;
		}; 
		if (args.MENU == "FTP Data") {
			return ftpData;
		};
		if (args.MENU == "Trade Return") {
			return tradeReturn;
		};
	};
	returnIsNewData(args) {
		if (args.TYPE == "Global") {
			return gotNewGlobalData;
		};
		if (args.TYPE == "Private") {
			return gotNewPrivateData;
		};
		if (args.TYPE == "Account") {
			return gotAccountData;
		};
		if (args.TYPE == "Coin") {
			return gotCoinData;
		};
		if (args.TYPE == "Disk") {
			return gotDiskData;
		};
		if (args.TYPE == "Trade") {
			return gotNewTrade;
		};
	}
	setMyName(args) {
		if (myName == "") {
			if (isRunning) {
				if (args.NAME != "") {
					if (!(userNames.indexOf(args.NAME) >= 0)) {
						if (args.NAME.length > 20) {
							return "Your username must be 20 characters or less!"
						} else {
							if (args.NAME.length != 0) {
								this.wss.send("<%sn>\n" + args.NAME); // begin packet data with setname command in the header
								myName = args.NAME;
								return "Set username on server successfully.";
							} else {
								return "You can't have a blank username!";
							}
						}
					} else {
						return "You can't have the same name as someone else!";
					}
				} else {
					return "You cannot have a blank username!";
				}
			} else {
				return "Connection closed, no action taken.";
			}
		} else {
			return "Username already set!";
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
	refreshUserList() {
		if (isRunning == true) {
			this.wss.send("<%rf>\n"); // begin packet data with global stream idenifier in the header
			return "Sent request successfully.";
		} else {
			return "Connection closed, no action taken.";
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
		if (args.TYPE == "Disk") {
			if (gotDiskData == true) {
				gotDiskData = false;
			};
		};
		if (args.TYPE == "Coin") {
			if (gotCoinData == true) {
				gotCoinData = false;
			};
		};
		if (args.TYPE == "Account") {
			if (gotCoinData == true) {
				gotCoinData = false;
			};
		};
	};
	//sendCMD(args) {
	//	if (isRunning) {
	//		if (myName != "") {
	//			if (args.user != myName) {
	//				this.wss.send("<%ps>\n" + myName + '\n'+args.user+'\n{"cmd":"'+args.cmd+'","id":"'+ myName+'", "data":"' + args.data + '"}\n');
	//				return "Sent command successfully.";
	//			} else {
	//				return "Can't send a command to yourself!";
	//			};
	//		} else {
	//			return "Username not set, no action taken.";
	//		}
	//	} else {
	//		return "Connection closed, no action taken.";
	//	};
	//};
	// CLOUDACCOUNT OPCODES
	doAcc(args) {
		if (args.ACCMODE == "Login") { 
			if (isRunning) {
				if (!isAuth) {
					accMode = "LI"
					this.wss.send("<%ps>\n" + myName + '\n%CA%\n{"cmd":"LOGIN","id":"'+ myName+'", "data":"'+args.pswd+'"}\n');
					return "Sent request successfully.";
				} else {
					return "Already logged in!";
				};
			} else {
				return "Connection closed, no action taken.";
			};
		};
		if (args.ACCMODE == "Register") {
			if (isRunning) {
				if (!isAuth) {
					accMode = "LI"
					this.wss.send("<%ps>\n" + myName + '\n%CA%\n{"cmd":"REGISTER","id":"'+ myName+'", "data":"'+args.pswd+'"}\n');
					return "Sent request successfully.";
				} else {
					return "Already logged in!";
				};
			} else {
				return "Connection closed, no action taken.";
			};
		};
	};
	logoutAcc() {
		if (isRunning) {
			if (isAuth) {
				accMode = "LO";
				this.wss.send("<%ps>\n" + myName + '\n%CA%\n{"cmd":"LOGOUT","id":"'+ myName+'", "data":""}\n');
				return "Sent request successfully.";
			} else {
				return "Already logged out!";
			};
		} else {
			return "Connection closed, no action taken.";
		};
	};
	checkAcc() {
		if (isRunning) {
				gotAccountData = false;
				this.wss.send("<%ps>\n" + myName + '\n%CA%\n{"cmd":"CHECK","id":"'+ myName+'", "data":""}\n');
				return "Sent request successfully.";
			} else {
				return "Connection closed, no action taken.";
		};
	};
	// CLOUDCOIN OPCODES
	checkBal() {
		if (myName != "") {
			if (userNames.indexOf('%CC%') >= 0) {
				if (isAuth) {
					this.wss.send("<%ps>\n" + myName + '\n%CC%\n{"cmd":"CHECK","id":"'+ myName+'", "data":""}\n');
					return "Sent request successfully.";
				} else {
						return "Not logged in!";
				}
			} else {
				return "CloudCoin API not connected! Try again later.";
			}
		} else {
			return "Username not set, no action taken.";
		};
	};
	setCoins(args) {
		if (isRunning) {
			if (args.coinmode == "Spend") {
				if (myName != "") {
					if (userNames.indexOf('%CC%') >= 0) {
						if (isAuth) {
							this.wss.send("<%ps>\n" + myName + '\n%CC%\n{"cmd":"SPEND","id":"'+ myName+'", "data":"' + String(args.coins) + '"}\n');
							return "Sent request successfully.";
						} else {
							return "Not logged in!";
						}
					} else {
						return "CloudCoin API not connected! Try again later.";
					}
				} else {
					return "Username not set, no action taken.";
				}
			}
			if (args.coinmode == "Earn") {
				if (myName != "") {
					if (userNames.indexOf('%CC%') >= 0) {
						if (isAuth) {
							this.wss.send("<%ps>\n" + myName + '\n%CC%\n{"cmd":"EARN","id":"'+ myName+'", "data":"' + String(args.coins) + '"}\n');
							return "Sent request successfully.";
						} else {
							return "Not logged in!";
						}
					} else {
						return "CloudCoin API not connected! Try again later.";
					}
				} else {
					return "Username not set, no action taken.";
				}
			}
		} else {
			return "Connection closed, no action taken."
		};
	};
	tradeCoins(args) {
		return "This block doesn't work yet. Sorry!"
	};
	// CLOUDDISK OPCODES
	getFTPFileList(){
		if (isRunning) {
			if (isAuth) {
				this.wss.send("<%ftp>\n" + myName + '\n%CD%\n{"cmd":"GETLIST","id":"'+ myName+'", "data":""}\n');
				return "Sent request successfully.";
			} else {
				return "Not Logged In!";
			};
		} else {
			return "Connection closed, no action taken.";
		};
	};
	getFTPFileInfo(args){
		if (isRunning) {
			if (isAuth) {
				this.wss.send("<%ftp>\n" + myName + '\n%CD%\n{"cmd":"GETINFO","id":"'+ myName+'", "data":"'+args.fname+'"}\n');
				return "Sent request successfully.";
			} else {
				return "Not Logged In!";
			};
		} else {
			return "Connection closed, no action taken.";
		};
	};
	initFTP(args){
		if (isRunning) {
			if (isAuth) {
				if (!runningFtp){
					ftpData = '';
					this.wss.send("<%ftp>\n" + myName + '\n%CD%\n{"cmd":"GET","id":"'+ myName+'", "data":"'+args.fname+'"}\n');
					runningFtp = true;
					return "Sent request successfully.";
				} else {
					return "Already running FTP!";
				}
			} else {
				return "Not Logged In!";
			};
		} else {
			return "Connection closed, no action taken.";
		};
	};
	abortFTP(){
		if (isRunning) {
			if (isAuth) {
				if (runningFtp){
					this.wss.send("<%ftp>\n" + myName + '\n%CD%\n{"cmd":"ABORT","id":"'+ myName+'", "data":""}\n');
					runningFtp = false;
					ftpData = '';
					return "Sent request successfully.";
				} else {
					return "Stopped FTP!"
				}
			} else {
				return "Not Logged In!";
			};
		} else {
			return "Connection closed, no action taken.";
		};
	};
	readData(args) {
		if (isRunning == true) {
			if (myName != "") {
				if (userNames.indexOf('%CD%') >= 0) {
					if (isAuth) {
						this.wss.send("<%ps>\n" + myName + '\n%CD%\n{"cmd":"READ","id":"'+ myName+'", "data":"' + args.slot + '"}\n');
						return "Sent request successfully.";
					} else {
						return "Not logged in!";
					}
				}
				else {
					return "CloudDisk API not connected! Try again later.";
				}
			} else {
				return "Username not set, no action taken.";
			}
		} else {
			return "Connection closed, no action taken.";
		};
	};
	writeData(args) {
		if (isRunning == true) {
			if (myName != "") {
				if (userNames.indexOf('%CD%') >= 0) {
					if (isAuth) {
						this.wss.send("<%ps>\n" + myName + '\n%CD%\n{"cmd":"WRITE","id":"'+ myName+'", "data":{"slot":"' + args.slot + '", "data":"'+args.data+'"}}\n');
						return "Sent request successfully.";
					} else {
						return "Not logged in!";
					}
				}
				else {
					return "CloudDisk API not connected! Try again later.";
				}
			} else {
				return "Username not set, no action taken.";
			}
		} else {
			return "Connection closed, no action taken.";
		};
	};
}

console.log("[CloudLink] Loading 3/3: Adding extension to ScratchBlocks...")
Scratch.extensions.register(new cloudlink());
console.log("[CloudLink] Loaded CloudLink successfully. You are running version v"+ vers);