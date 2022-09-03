var servers = {}; ; // Server list
let mWS = null;

// Get the server URL list
try {
	fetch('https://mikedev101.github.io/cloudlink/serverlist.json').then(response => {
		return response.text();
	}).then(data => {
		servers = JSON.parse(data);
	}).catch(err => {
		console.log(err);
        servers = {};
	});
} catch(err) {
	console.log(err);
    servers = {};
};

function jsonCheck(JSON_STRING) {
    try {
        JSON.parse(JSON_STRING);
        return true;
    } catch (err) {
        return false;
    }
}

class CloudLink {
    constructor (runtime, extensionId) {
        // Extension stuff
		this.runtime = runtime;
        this.cl_icon = 'data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0idXRmLTgiPz4NCjwhLS0gR2VuZXJhdG9yOiBBZG9iZSBJbGx1c3RyYXRvciAyNS4yLjMsIFNWRyBFeHBvcnQgUGx1Zy1JbiAuIFNWRyBWZXJzaW9uOiA2LjAwIEJ1aWxkIDApICAtLT4NCjxzdmcgdmVyc2lvbj0iMS4xIiBpZD0iTGF5ZXJfMSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiB4bWxuczp4bGluaz0iaHR0cDovL3d3dy53My5vcmcvMTk5OS94bGluayIgeD0iMHB4IiB5PSIwcHgiDQoJIHZpZXdCb3g9IjAgMCA0NSA0NSIgc3R5bGU9ImVuYWJsZS1iYWNrZ3JvdW5kOm5ldyAwIDAgNDUgNDU7IiB4bWw6c3BhY2U9InByZXNlcnZlIj4NCjxzdHlsZSB0eXBlPSJ0ZXh0L2NzcyI+DQoJLnN0MHtmaWxsOiMwRkJEOEM7fQ0KCS5zdDF7ZmlsbDpub25lO3N0cm9rZTojRkZGRkZGO3N0cm9rZS13aWR0aDo0O3N0cm9rZS1saW5lY2FwOnJvdW5kO3N0cm9rZS1saW5lam9pbjpyb3VuZDtzdHJva2UtbWl0ZXJsaW1pdDoxMDt9DQo8L3N0eWxlPg0KPGcgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoLTIxNy41MDAxNCwtMTU3LjUwMDEzKSI+DQoJPGc+DQoJCTxwYXRoIGNsYXNzPSJzdDAiIGQ9Ik0yMTcuNSwxODBjMC0xMi40LDEwLjEtMjIuNSwyMi41LTIyLjVzMjIuNSwxMC4xLDIyLjUsMjIuNXMtMTAuMSwyMi41LTIyLjUsMjIuNVMyMTcuNSwxOTIuNCwyMTcuNSwxODANCgkJCUwyMTcuNSwxODB6Ii8+DQoJCTxnPg0KCQkJPHBhdGggY2xhc3M9InN0MSIgZD0iTTIzMC4zLDE4MC4xYzUuNy00LjcsMTMuOS00LjcsMTkuNiwwIi8+DQoJCQk8cGF0aCBjbGFzcz0ic3QxIiBkPSJNMjI1LjMsMTc1LjFjOC40LTcuNCwyMS03LjQsMjkuNCwwIi8+DQoJCQk8cGF0aCBjbGFzcz0ic3QxIiBkPSJNMjM1LjIsMTg1YzIuOS0yLjEsNi44LTIuMSw5LjcsMCIvPg0KCQkJPHBhdGggY2xhc3M9InN0MSIgZD0iTTI0MCwxOTAuNEwyNDAsMTkwLjQiLz4NCgkJPC9nPg0KCTwvZz4NCjwvZz4NCjwvc3ZnPg0K';
		this.cl_block = 'data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0idXRmLTgiPz4NCjwhLS0gR2VuZXJhdG9yOiBBZG9iZSBJbGx1c3RyYXRvciAyNS4yLjMsIFNWRyBFeHBvcnQgUGx1Zy1JbiAuIFNWRyBWZXJzaW9uOiA2LjAwIEJ1aWxkIDApICAtLT4NCjxzdmcgdmVyc2lvbj0iMS4xIiBpZD0iTGF5ZXJfMSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiB4bWxuczp4bGluaz0iaHR0cDovL3d3dy53My5vcmcvMTk5OS94bGluayIgeD0iMHB4IiB5PSIwcHgiDQoJIHZpZXdCb3g9IjAgMCA0NSA0NSIgc3R5bGU9ImVuYWJsZS1iYWNrZ3JvdW5kOm5ldyAwIDAgNDUgNDU7IiB4bWw6c3BhY2U9InByZXNlcnZlIj4NCjxzdHlsZSB0eXBlPSJ0ZXh0L2NzcyI+DQoJLnN0MHtmaWxsOm5vbmU7c3Ryb2tlOiNGRkZGRkY7c3Ryb2tlLXdpZHRoOjQ7c3Ryb2tlLWxpbmVjYXA6cm91bmQ7c3Ryb2tlLWxpbmVqb2luOnJvdW5kO3N0cm9rZS1taXRlcmxpbWl0OjEwO30NCjwvc3R5bGU+DQo8Zz4NCgk8cGF0aCBjbGFzcz0ic3QwIiBkPSJNMTIuOCwyMi42YzUuNy00LjcsMTMuOS00LjcsMTkuNiwwIi8+DQoJPHBhdGggY2xhc3M9InN0MCIgZD0iTTcuOCwxNy42YzguNC03LjQsMjEtNy40LDI5LjQsMCIvPg0KCTxwYXRoIGNsYXNzPSJzdDAiIGQ9Ik0xNy43LDI3LjVjMi45LTIuMSw2LjgtMi4xLDkuNywwIi8+DQoJPHBhdGggY2xhc3M9InN0MCIgZD0iTTIyLjUsMzIuOUwyMi41LDMyLjkiLz4NCjwvZz4NCjwvc3ZnPg0K';
		
        // Socket data
		this.socketData = {
            "gmsg": [],
            "pmsg": [],
            "direct": [],
            "statuscode": [],
            "gvar": [],
            "pvar": [],
            "motd": "",
            "client_ip": "",
            "ulist": [],
            "server_version": ""
        };
        this.varData = {
            "gvar": {},
            "pvar": {}
        };

        this.queueableCmds = ["gmsg", "pmsg", "gvar", "pvar", "direct", "statuscode"];
        this.varCmds = ["gvar", "pvar"];
    
        // Listeners
        this.socketListeners = {};
		this.newSocketData = {
			"gmsg": false,
			"pmsg": false,
			"direct": false,
			"statuscode": false,
			"gvar": false,
			"pvar": false
		};
		
        // Edge-triggered hat blocks
		this.connect_hat = 0;
		this.packet_hat = 0;
		this.close_hat = 0;
        
        // Status stuff
        this.isRunning = false;
        this.isLinked = false;
        this.version = "S4.0";
		this.link_status = 0;
        this.username = "";
		this.tmp_username = "";
		this.isUsernameSyncing = false;
		this.disconnectWasClean = false;
		this.wasConnectionDropped = false;
        this.didConnectionFail = false;

        // Listeners stuff
        this.enableListener = false;
        this.setListener = "";
        
        // Remapping stuff
        this.menuRemap = {
            "Global data": "gmsg",
            "Private data": "pmsg",
            "Global variables": "gvar",
            "Private variables": "pvar",
            "Direct data": "direct",
            "Status code": "statuscode",
            "All data": "all"
        };
    }

    getInfo () {
        return {
            "id": 'cloudlink',
            "name": 'CloudLink',
			"blockIconURI": this.cl_block,
			"menuIconURI": this.cl_icon,
            "blocks": [
				{
                	"opcode": 'returnGlobalData',
                    "blockType": "reporter",
                    "text": "Global data"
                },
                {
                	"opcode": 'returnPrivateData',
                    "blockType": "reporter",
                    "text": "Private data"
                },
				{
                	"opcode": 'returnDirectData',
                    "blockType": "reporter",
                    "text": "Direct Data"
                },
				{
                	"opcode": 'returnLinkData',
                    "blockType": "reporter",
                    "text": "Link status"
                },
				{
                	"opcode": 'returnStatusCode',
                    "blockType": "reporter",
                    "text": "Status code"
                },
				{
					"opcode": 'returnUserListData', 
					"blockType": "reporter",
					"text": "Usernames"
				},
                {
                    "opcode": "returnUsernameData",
                    "blockType": "reporter",
                    "text": "My username"
                },
                {
                    "opcode": "returnVersionData",
                    "blockType": "reporter",
                    "text": "Extension version"
                },
                {
                    "opcode": "returnServerVersion",
                    "blockType": "reporter",
                    "text": "Server version"
                },
                {
                    "opcode": "returnServerList",
                    "blockType": "reporter",
                    "text": "Server list"
                },
                {
                    "opcode": "returnMOTD",
                    "blockType": "reporter",
                    "text": "Server MOTD"
                },
                {
                    "opcode": "returnClientIP",
                    "blockType": "reporter",
                    "text": "My IP address"
                },
                {
                    "opcode": "readQueueSize",
                    "blockType": "reporter",
                    "text": "Size of queue for [TYPE]",
                    "arguments": {
                        "TYPE": {
                            "type": "string",
                            "menu": "allmenu",
                            "defaultValue": "All data",
                        },
                    },
                },
				{
                    "opcode": "readQueueData",
                    "blockType": "reporter",
                    "text": "Packet queue for [TYPE]",
                    "arguments": {
                        "TYPE": {
                            "type": "string",
                            "menu": "allmenu",
                            "defaultValue": "All data",
                        },
                    },
                },
                {
                    "opcode": 'returnVarData',
                    "blockType": "reporter",
                    "text": "[TYPE] [VAR] data",
                    "arguments": {
                        "VAR": {
                            "type": "string",
                            "defaultValue": "Apple",
                        },
                        "TYPE": {
                            "type": "string",
                            "menu": "varmenu",
                            "defaultValue": "Global variables",
                        },
                    },
                },
                {
					"opcode": 'parseJSON',
					"blockType": "reporter",
					"text": '[PATH] of [JSON_STRING]',
					"arguments": {
						"PATH": {
							"type": "string",
							"defaultValue": 'fruit/apples',
						},
						"JSON_STRING": {
							"type": "string",
							"defaultValue": '{"fruit": {"apples": 2, "bananas": 3}, "total_fruit": 5}',
						},
					},
				},
                {
					"opcode": 'getFromJSONArray',
					"blockType": "reporter",
					"text": 'Get [NUM] from JSON array [ARRAY]',
					"arguments": {
						"NUM": {
							"type": "number",
							"defaultValue": 0,
						},
						"ARRAY": {
							"type": "string",
							"defaultValue": '["foo","bar"]',
						}
					}
				},
                {
                    "opcode": 'fetchURL',
                    "blockType": "reporter",
                    "blockAllThreads": "true",
                    "text": "Fetch data from URL [url]",
                    "arguments": {
                        "url": {
                            "type": "string",
                            "defaultValue": "https://mikedev101.github.io/cloudlink/fetch_test",
                        },
                    },
                },
                {
					"opcode": 'requestURL', 
					"blockType": "reporter",
					"blockAllThreads": "true",
					"text": 'Send request with method [method] for URL [url] with data [data] and headers [headers]',
					"arguments": {
                        "method": {
							"type": "string",
							"defaultValue": 'GET',
						},
						"url": {
							"type": "string",
							"defaultValue": 'https://mikedev101.github.io/cloudlink/fetch_test',
						},
                        "data": {
                            "type": "string",
                            "defaultValue": '{}'
                        },
                        "headers": {
                            "type": "string",
                            "defaultValue": '{}'
                        },
					}
				},
                
                {
                	"opcode": 'makeJSON',
                    "blockType": "reporter",
                    "text": 'Convert [toBeJSONified] to JSON',
					"arguments": {
						"toBeJSONified": {
							"type": "string",
							"defaultValue": '{"test": true}',
						},
					}
                },
                {
                	"opcode": 'onConnect',
                    "blockType": "hat",
                    "text": 'When connected',
                    "blockAllThreads": "true"
                },
                {
                	"opcode": 'onClose',
                    "blockType": "hat",
                    "text": 'When disconnected',
                    "blockAllThreads": "true"
                },
                {
                	"opcode": 'onListener',
                    "blockType": "hat",
                    "text": 'When I receive new packet with listener [ID]',
                    "blockAllThreads": "true",
                    "arguments": {
                        "ID": {
                            "type": "string",
                            "defaultValue": "example-listener",
                        },
                    },
                },
                {
                    "opcode": 'onNewPacket',
                    "blockType": "hat",
                    "text": 'When I receive new [TYPE] packet',
                    "blockAllThreads": "true",
                    "arguments": {
                        "TYPE": {
                            "type": "string",
                            "menu": "almostallmenu",
                            "defaultValue": 'Global data'
                        },
                    },
                },
                {
                    "opcode": 'onNewVar',
                    "blockType": "hat",
                    "text": 'When I receive new [TYPE] data for [VAR]',
                    "blockAllThreads": "true",
                    "arguments": {
                        "TYPE": {
                            "type": "string",
                            "menu": "varmenu",
                            "defaultValue": 'Global variables',
                        },
                        "VAR": {
                            "type": "string",
                            "defaultValue": 'Apple',
                        },
                    },
                },
                {
                	"opcode": 'getComState',
                    "blockType": "Boolean",
                    "text": 'Connected?',
                },
                {
                    "opcode": 'getRoomState',
                    "blockType": "Boolean",
                    "text": 'Linked to rooms?',
                },
				{
                	"opcode": 'getComLostConnectionState',
                    "blockType": "Boolean",
                    "text": 'Lost connection?',
                },
				{
                	"opcode": 'getComFailedConnectionState',
                    "blockType": "Boolean",
                    "text": 'Failed to connnect?',
                },
                {
                	"opcode": 'getUsernameState',
                    "blockType": "Boolean",
                    "text": 'Username synced?',
                },
                {
                	"opcode": 'returnIsNewData',
                    "blockType": "Boolean",
                    "text": 'Got New [TYPE]?',
					"arguments": {
						"TYPE": {
							"type": "string",
                            "menu": "datamenu",
							"defaultValue": 'Global data',
						},
					},
                },
                {
                	"opcode": 'returnIsNewVarData',
                    "blockType": "Boolean",
                    "text": 'Got New [TYPE] data for variable [VAR]?',
					"arguments": {
						"TYPE": {
							"type": "string",
                            "menu": "varmenu",
							"defaultValue": 'Global variables',
						},
                        "VAR": {
                            "type": "string",
							"defaultValue": 'Apple',
                        },
					},
                },
                {
                    "opcode": 'returnIsNewListener',
                    "blockType": "Boolean",
                    "text": 'Got new packet with listener [ID]?',
                    "blockAllThreads": "true",
                    "arguments": {
                        "ID": {
                            "type": "string",
                            "defaultValue": "example-listener",
                        },
                    },
                },
                {
                	"opcode": 'checkForID',
                    "blockType": "Boolean",
                    "text": 'ID [ID] connected?',
					"arguments": {
						"ID": {
							"type": "string",
							"defaultValue": 'Another name',
						},
					},
                },
				{
                	"opcode": 'isValidJSON',
                    "blockType": "Boolean",
                    "text": 'Is [JSON_STRING] valid JSON?',
					"arguments": {
						"JSON_STRING": {
							"type": "string",
							"defaultValue": '{"fruit": {"apples": 2, "bananas": 3}, "total_fruit": 5}',
						},
					},
                },
                {
                    "opcode": 'openSocket',
                    "blockType": "command",
                    "text": 'Connect to [IP]',
					"blockAllThreads": "true",
					"arguments": {
						"IP": {
							"type": "string",
							"defaultValue": 'ws://127.0.0.1:3000/',
						},
					},
                },
                {
                    "opcode": 'openSocketPublicServers',
                    "blockType": "command",
                    "text": 'Connect to server [ID]',
					"blockAllThreads": "true",
					"arguments": {
						"ID": {
							"type": "number",
							"defaultValue": '',
						},
					},
                },
                {
                	"opcode": 'closeSocket',
                    "blockType": "command",
					"blockAllThreads": "true",
                    "text": 'Disconnect',
                },
                {
                    "opcode": 'setMyName',
                    "blockType": "command",
                    "text": 'Set [NAME] as username',
                    "blockAllThreads": "true",
					"arguments": {
						"NAME": {
							"type": "string",
							"defaultValue": "A name",
						},
					},
                },
                {
                    "opcode": 'createListener',
                    "blockType": "command",
                    "text": 'Attach listener [ID] to next packet',
                    "blockAllThreads": "true",
                    "arguments": {
                        "ID": {
                            "type": "string",
                            "defaultValue": "example-listener",
                        },
                    },
                },
                {
                    "opcode": 'linkToRooms',
                    "blockType": "command",
                    "text": 'Link to room(s) [ROOMS]',
                    "blockAllThreads": "true",
                    "arguments": {
                        "ROOMS": {
                            "type": "string",
                            "defaultValue": '["Test"]',
                        },
                    }
                },
                {
                    "opcode": 'unlinkFromRooms',
                    "blockType": "command",
                    "text": 'Unlink from all rooms',
                    "blockAllThreads": "true"
                },
                {
                	"opcode": 'sendGData',
                    "blockType": "command",
                    "text": 'Send [DATA]',
					"blockAllThreads": "true",
                    "arguments": {
                        "DATA": {
                            "type": "string",
                            "defaultValue": 'Apple'
                        }
                    }
                },
                {
                	"opcode": 'sendPData',
                    "blockType": "command",
                    "text": 'Send [DATA] to [ID]',
					"blockAllThreads": "true",
                    "arguments": {
                        "DATA": {
                            "type": "string",
                            "defaultValue": 'Apple'
                        },
                        "ID": {
                            "type": "string",
                            "defaultValue": 'Another name'
                        }
                    }
                },
                {
                	"opcode": 'sendGDataAsVar',
                    "blockType": "command",
                    "text": 'Send variable [VAR] with data [DATA]',
					"blockAllThreads": "true",
                    "arguments": {
                        "DATA": {
                            "type": "string",
                            "defaultValue": 'Banana'
                        },
                        "VAR": {
                            "type": "string",
                            "defaultValue": 'Apple'
                        }
                    }
                },
                {
                	"opcode": 'sendPDataAsVar',
                    "blockType": "command",
                    "text": 'Send variable [VAR] to [ID] with data [DATA]',
					"blockAllThreads": "true",
                    "arguments": {
                        "DATA": {
                            "type": "string",
                            "defaultValue": 'Banana'
                        },
                        "ID": {
                            "type": "string",
                            "defaultValue": 'Another name'
                        },
                        "VAR": {
                            "type": "string",
                            "defaultValue": 'Apple'
                        }
                    }
                },
                {
                	"opcode": 'runCMD',
                    "blockType": "command",
                    "text": 'Send command [CMD] [ID] [DATA]',
					"blockAllThreads": "true",
                    "arguments": {
                        "CMD": {
                            "type": "string",
                            "defaultValue": 'direct'
                        },
                        "ID": {
                            "type": "string",
                            "defaultValue": 'id'
                        },
                        "DATA": {
                            "type": "string",
                            "defaultValue": 'val'
                        }
                    }
                },
                {
                	"opcode": 'resetNewData',
                    "blockType": "command",
                    "text": 'Reset got new [TYPE] status',
					"blockAllThreads": "true",
                    "arguments": {
                        "TYPE": {
                            "type": "string",
                            "menu": "datamenu",
                            "defaultValue": 'Global data'
                        }
                    }
                },
                {
                	"opcode": 'resetNewVarData',
                    "blockType": "command",
                    "text": 'Reset got new [TYPE] [VAR] status',
					"blockAllThreads": "true",
                    "arguments": {
                        "TYPE": {
                            "type": "string",
                            "menu": "varmenu",
                            "defaultValue": 'Global variables'
                        },
                        "VAR": {
                            "type": "string",
                            "defaultValue": 'Apple'
                        }
                    }
                },
                {
                    "opcode": 'resetNewListener',
                    "blockType": "command",
                    "text": 'Reset got new [ID] listener status',
                    "blockAllThreads": "true",
                    "arguments": {
                        "ID": {
                            "type": "string",
                            "defaultValue": 'example-listener'
                        }
                    }
                },
                {
	                "opcode": 'clearAllPackets',
                    "blockType": "command",
                    "text": "Clear all packets for [TYPE]",
                    "arguments": {
                        "TYPE": {
                            "type": "string",
                            "menu": "allmenu",
                            "defaultValue": "All data"
                        },
                    },
                }
			],
            "menus": {
                "coms": {
                    "items": ["Connected", "Username synced"]
                },
                "datamenu": {
                    "items": ['Global data', 'Private data', 'Direct data', 'Status code']
                },
                "varmenu": {
                    "items": ['Global variables', 'Private variables']
                },
                "allmenu": {
                    "items": ['Global data', 'Private data', 'Direct data', 'Status code', "Global variables", "Private variables", "All data"]
                },
                "almostallmenu": {
                    "items": ['Global data', 'Private data', 'Direct data', 'Status code', "Global variables", "Private variables"]
                },
            },
        };
    };
    
    // Code for blocks go here
    
    returnGlobalData() {
        if (this.socketData.gmsg.length != 0) {

            let data = (this.socketData.gmsg[this.socketData.gmsg.length - 1].val);

            if (typeof(data) == "object") {
                data = JSON.stringify(data); // Make the JSON safe for Scratch
            }

        	return data;
		} else {
			return "";
		};
    };
    
    returnPrivateData() {
		if (this.socketData.pmsg.length != 0) {
            let data = (this.socketData.pmsg[this.socketData.pmsg.length - 1].val);

            if (typeof (data) == "object") {
                data = JSON.stringify(data); // Make the JSON safe for Scratch
            }

            return data;
		} else {
			return "";
		};
    };
    
    returnDirectData() {
        if (this.socketData.direct.length != 0) {
            let data = (this.socketData.direct[this.socketData.direct.length - 1].val);

            if (typeof (data) == "object") {
                data = JSON.stringify(data); // Make the JSON safe for Scratch
            }

            return data;
		} else {
			return "";
		};
    };
    
    returnLinkData() {
        return String(this.link_status);
    };
    
    returnStatusCode() {
		if (this.socketData.statuscode.length != 0) {
            let data = (this.socketData.statuscode[this.socketData.statuscode.length - 1].code);

            if (typeof (data) == "object") {
                data = JSON.stringify(data); // Make the JSON safe for Scratch
            }

            return data;
		} else {
			return "";
		};
    };
    
    returnUserListData() {
        return JSON.stringify(this.socketData.ulist);
    };
    
    returnUsernameData() {
        let data = this.username;

        if (typeof (data) == "object") {
            data = JSON.stringify(data); // Make the JSON safe for Scratch
        }

        return data;
    };
    
    returnVersionData() {
        return String(this.version);
    };
    
    returnServerVersion() {
        return String(this.socketData.server_version);
    };
    
    returnServerList() {
        return JSON.stringify(servers);
    };
    
    returnMOTD() {
        return String(this.socketData.motd);
    };
    
    returnClientIP() {
        return String(this.socketData.client_ip);
    };
	
    readQueueSize({TYPE}) {
		if (this.menuRemap[String(TYPE)] == "all") {
			let tmp_size = 0;
			tmp_size = tmp_size + this.socketData.gmsg.length;
			tmp_size = tmp_size + this.socketData.pmsg.length;
			tmp_size = tmp_size + this.socketData.direct.length;
			tmp_size = tmp_size + this.socketData.statuscode.length;
			tmp_size = tmp_size + this.socketData.gvar.length;
			tmp_size = tmp_size + this.socketData.pvar.length;
			return tmp_size;
		} else {
        	return this.socketData[this.menuRemap[String(TYPE)]].length;
		};
    };
    
	readQueueData({TYPE}) {
		if (this.menuRemap[String(TYPE)] == "all") {
			let tmp_socketData = JSON.parse(JSON.stringify(this.socketData)); // Deep copy
			
			delete tmp_socketData.motd;
			delete tmp_socketData.client_ip;
			delete tmp_socketData.ulist;
			delete tmp_socketData.server_version;
			
			return JSON.stringify(tmp_socketData);
		} else {
        	return JSON.stringify(this.socketData[this.menuRemap[String(TYPE)]]);
		};
    };
	
    returnVarData({ TYPE, VAR }) {
        if (this.isRunning) {
            if (self.varData.hasOwnProperty(this.menuRemap[TYPE])) {
                if (self.varData[this.menuRemap[TYPE]].hasOwnProperty(VAR)) {
                    return self.varData[this.menuRemap[TYPE]][VAR].value;
                } else {
                    return "";
                };
            } else {
                return "";
            };
        } else {
            return "";
        }
    };
    
    parseJSON({PATH, JSON_STRING}) {
		try {
			const path = PATH.toString().split('/').map(prop => decodeURIComponent(prop));
			if (path[0] === '') path.splice(0, 1);
			if (path[path.length - 1] === '') path.splice(-1, 1);
			let json;
			try {
				json = JSON.parse(' ' + JSON_STRING);
			} catch (e) {
				return e.message;
			};
			path.forEach(prop => json = json[prop]);
			if (json === null) return 'null';
			else if (json === undefined) return '';
			else if (typeof json === 'object') return JSON.stringify(json);
			else return json.toString();
		} catch (err) {
			return '';
		};
	};
    
    getFromJSONArray({NUM, ARRAY}) {
        var json_array = JSON.parse(ARRAY);
        if (json_array[NUM] == "undefined") {
            return "";
        } else {
            let data = json_array[NUM];

            if (typeof (data) == "object") {
                data = JSON.stringify(data); // Make the JSON safe for Scratch
            }

            return data;
        }
    };
    
    fetchURL(args) {
		return fetch(args.url, {
            method: "GET"
        }).then(response => response.text());
	};
    
    requestURL(args) {
        if (args.method == "GET" || args.method == "HEAD") {
            return fetch(args.url, {
                method: args.method,
                headers: JSON.parse(args.headers)
            }).then(response => response.text());
        } else {
            return fetch(args.url, {
                method: args.method,
                headers: JSON.parse(args.headers),
                body: JSON.parse(args.data)
            }).then(response => response.text());
        } 
	};
    
    isValidJSON({JSON_STRING}) {
        return jsonCheck(JSON_STRING);
	};
    
    makeJSON({toBeJSONified}) {
		if (typeof(toBeJSONified) == "string") {
			try {
				JSON.parse(toBeJSONified);
				return String(toBeJSONified);
			} catch(err) {
				return "Not JSON!";
			}
		} else if (typeof(toBeJSONified) == "object") {
			return JSON.stringify(toBeJSONified);
		} else {
			return "Not JSON!";
		};
	};
	
    onConnect() {
		const self = this;
		if (self.connect_hat == 0 && self.isRunning) {
			self.connect_hat = 1;
			return true;
		} else {
			return false;
		};
	};
    
    onClose() {
		const self = this;
		if (self.close_hat == 0 && !self.isRunning) {
			self.close_hat = 1;
			return true;
		} else {
			return false;
		};
    };

    onListener({ ID }) {
        const self = this;
        if ((this.isRunning) && (this.socketListeners.hasOwnProperty(String(ID)))) {
            if (self.socketListeners[String(ID)]) {
                self.socketListeners[String(ID)] = false;
                return true;
            } else {
                return false;
            };
        } else {
            return false;
        };
    };

    onNewPacket({ TYPE }) {
        const self = this;
        if ((this.isRunning) && (this.newSocketData[this.menuRemap[String(TYPE)]])) {
            self.newSocketData[this.menuRemap[String(TYPE)]] = false;
            return true;
        } else {
            return false;
        };
    };

    onNewVar({ TYPE, VAR }) {
        if (this.isRunning) {
            if (self.varData.hasOwnProperty(this.menuRemap[TYPE])) {
                if (self.varData[this.menuRemap[TYPE]].hasOwnProperty(VAR)) {
                    if (self.varData[this.menuRemap[TYPE]][VAR].isNew) {
                        self.varData[this.menuRemap[TYPE]][VAR].isNew = false;
                        return true;
                    } else {
                        return false;
                    }
                } else {
                    return false;
                };
            } else {
                return false;
            };
        } else {
            return false;
        };
    };

    getComState(){
        return String(this.link_status == 2);
    };

    getRoomState() {
        return this.isLinked;
    };

	getComLostConnectionState() {
		return this.wasConnectionDropped;
	};
	
	getComFailedConnectionState() {
		return this.didConnectionFail;
	};
    
    getUsernameState(){
        return ((this.username != "") && (this.socketData.ulist.includes(String(this.username))));
    };
    
    returnIsNewData({TYPE}){
        if (this.isRunning) {
			return this.newSocketData[this.menuRemap[String(TYPE)]];
		} else {
			return false;
		};
    };

    returnIsNewVarData({ TYPE, VAR }) {
        if (this.isRunning) {
            if (self.varData.hasOwnProperty(this.menuRemap[TYPE])) {
                if (self.varData[this.menuRemap[TYPE]].hasOwnProperty(VAR)) {
                    return self.varData[this.menuRemap[TYPE]][VAR].isNew;
                } else {
                    return false;
                };
            } else {
                return false;
            };
        } else {
            return false;
        };
    };

    returnIsNewListener({ ID }) {
        if (this.isRunning) {
            if (this.socketListeners.hasOwnProperty(String(ID))) {
                return this.socketListeners[ID];
            } else {
                return false;
            };
        } else {
            return false;
        };
    };

    checkForID({ ID }) {
        // Thanks StackOverflow!
        if (jsonCheck(ID)) {
            console.log(this.socketData.ulist)
            return this.socketData.ulist.some(o => ((o.username === JSON.parse(ID).username) || (o.id == JSON.parse(ID).id)));
        } else {
            return false;
        };
    };
    
    openSocket({IP}) {
		const self = this;
    	if (!self.isRunning) {
    		console.log("Starting socket.");
			self.link_status = 1;
			
			self.disconnectWasClean = false;
			self.wasConnectionDropped = false;
			self.didConnectionFail = false;
			
    		mWS = new WebSocket(String(IP));
    		
    		mWS.onerror = function(){
    			self.isRunning = false;
    		};
			
    		mWS.onopen = function(){
    			self.isRunning = true;
				self.packet_queue = {};
				self.link_status = 2;
    			console.log("Successfully opened socket.");
    		};
			
			mWS.onmessage = function(event){
   				let tmp_socketData = JSON.parse(event.data);
                console.log("RX:", tmp_socketData);

                if (self.queueableCmds.includes(tmp_socketData.cmd)) {
                    self.socketData[tmp_socketData.cmd].push(tmp_socketData);
				} else {
					self.socketData[tmp_socketData.cmd] = tmp_socketData.val;
				};
				
				if (self.newSocketData.hasOwnProperty(tmp_socketData.cmd)) {
					self.newSocketData[tmp_socketData.cmd] = true;
				};
				
                if (self.varCmds.includes(tmp_socketData.cmd)) {
                    self.varData[tmp_socketData.cmd][tmp_socketData.name] = {
                        "value": tmp_socketData.val,
                        "isNew": true
                    };
                };

				if (tmp_socketData.hasOwnProperty("listener")) {
					if (tmp_socketData.listener == "setusername") {
						if (tmp_socketData.code == "I:100 | OK") {
                            self.username = tmp_socketData.val;
							self.isUsernameSyncing = false;
							console.log("Username was accepted by the server, and has been set to:", self.username);
						} else {
                            console.warn("Username was rejected by the server. Error code:", String(tmp_socketData.statuscode));
							self.isUsernameSyncing = false;
						};
					} else {
						if (self.socketListeners.hasOwnProperty(tmp_socketData.listener)) {
							self.socketListeners[tmp_socketData.listener] = true;
						};
					};
				};
				self.packet_hat = 0;
   			};
			
			mWS.onclose = function() {
				self.isRunning = false;
				self.connect_hat = 0;
				self.packet_hat = 0;
				if (self.close_hat == 1) {
					self.close_hat = 0;
				};
				self.socketData = {
					"gmsg": [],
					"pmsg": [],
					"direct": [],
					"statuscode": [],
					"gvar": [],
					"pvar": [],
					"motd": "",
					"client_ip": "",
					"ulist": [],
					"server_version": ""
				};
				self.newSocketData = {
					"gmsg": false,
					"pmsg": false,
					"direct": false,
					"statuscode": false,
					"gvar": false,
					"pvar": false
				};
				self.socketListeners = {};
				self.username = "";
				self.tmp_username = "";
				self.isUsernameSyncing = false;
				if (self.link_status != 1) {
					if (self.disconnectWasClean) {
						self.link_status = 3;
						console.log("Socket closed.");
						self.wasConnectionDropped = false;
						self.didConnectionFail = false;
					} else {
						self.link_status = 4;
						console.error("Lost connection to the server.");
						self.wasConnectionDropped = true;
						self.didConnectionFail = false;
					};
				} else {
					self.link_status = 4;
					console.error("Failed to connect to server.");
					self.wasConnectionDropped = false;
					self.didConnectionFail = true;
				};
			};
    	} else {
    		console.warn("Socket is already open.");
    	};
    }
    
    openSocketPublicServers({ ID }){
        if (servers.hasOwnProperty(ID)) {
            console.log("Connecting to:", servers[ID].url)
            this.openSocket({"IP": servers[ID].url});
        };
    };
    
    closeSocket(){
		const self = this;
        if (this.isRunning) {
    		console.log("Closing socket...");
    		mWS.close(1000,'script closure');
			self.disconnectWasClean = true;
    	} else {
    		console.warn("Socket is not open.");
    	};
    }
    
    setMyName({NAME}) {
		const self = this;
		if (this.isRunning) {
			if (!this.isUsernameSyncing) {
				if (this.username == ""){
					if (String(NAME) != "") {
						if ((!(String(NAME).length > 20))) {
							if (!(String(NAME) == "%CA%" || String(NAME) == "%CC%" || String(NAME) == "%CD%" || String(NAME) == "%MS%")){
                                let tmp_msg = {
                                    cmd: "setid",
                                    val: String(NAME),
                                    listener: "setusername"
                                };

                                console.log("TX:", tmp_msg);
                                mWS.send(JSON.stringify(tmp_msg));
								
								self.tmp_username = String(NAME);
								self.isUsernameSyncing = true;
									
							} else {
								console.log("Blocking attempt to use reserved usernames");
							};
						} else {
							console.log("Blocking attempt to use username larger than 20 characters, username is " + String(NAME).length + " characters long");
						};
					} else {
						console.log("Blocking attempt to use blank username");
					};
				} else {
					console.warn("Username already has been set!");
				};
			} else {
				console.warn("Username is still syncing!");
			};
		};
    };

    createListener({ ID }) {
        self = this;
        if (this.isRunning) {
            self.enableListener = true;
            self.setListener = String(ID);
        } else {
            console.log("Cannot assign a listener to a packet while disconnected");
        };
    };

    linkToRooms({ ROOMS }) {
        const self = this;
        if (this.isRunning) {
            if (!(String(ROOMS).length > 1000)) {
                let tmp_msg = {
                    cmd: "link",
                    val: ROOMS
                };

                if (this.enableListener) {
                    tmp_msg["listener"] = String(this.setListener);
                };

                console.log("TX:", tmp_msg);
                mWS.send(JSON.stringify(tmp_msg));

                if (this.enableListener) {
                    if (!self.socketListeners.hasOwnProperty(this.setListener)) {
                        self.socketListeners[this.setListener] = false;
                    };
                    self.enableListener = false;
                };

                if (!(this.isLinked)) {
                    self.isLinked = true;
                };

            } else {
                console.warn("Blocking attempt to send a room ID / room list larger than 1000 bytes (1 KB), room ID / room list is " + String(ROOMS).length + " bytes");
            };
        } else {
            console.warn("Socket is not open.");
        };
    };

    unlinkFromRooms() {
        const self = this;
        if (this.isRunning) {
            if (this.isLinked) {
                let tmp_msg = {
                    cmd: "unlink",
                    val: ""
                };

                if (this.enableListener) {
                    tmp_msg["listener"] = String(this.setListener);
                };

                console.log("TX:", tmp_msg);
                mWS.send(JSON.stringify(tmp_msg));

                if (this.enableListener) {
                    if (!self.socketListeners.hasOwnProperty(this.setListener)) {
                        self.socketListeners[this.setListener] = false;
                    };
                    self.enableListener = false;
                };

                self.isLinked = false;
            } else {
                console.warn("Not linked to any rooms!");
            };
        } else {
            console.warn("Socket is not open.");
        };
    };

    sendGData({DATA}){
		const self = this;
        if (this.isRunning) {
    		if (!(String(DATA).length > 1000)) {
                let tmp_msg = {
                    cmd: "gmsg",
                    val: DATA
                };

                if (this.enableListener) {
                    tmp_msg["listener"] = String(this.setListener);
                };

				console.log("TX:", tmp_msg);
                mWS.send(JSON.stringify(tmp_msg));

                if (this.enableListener) {
                    if (!self.socketListeners.hasOwnProperty(this.setListener)) {
                        self.socketListeners[this.setListener] = false;
                    };
                    self.enableListener = false;
                };
				
			} else {
				console.warn("Blocking attempt to send packet larger than 1000 bytes (1 KB), packet is " + String(DATA).length + " bytes");
			};
    	} else {
    		console.warn("Socket is not open.");
    	};
    };
    
    sendPData({DATA, ID}) {
		const self = this;
        if (this.isRunning) {
            if (!(String(DATA).length > 1000)) {
                let tmp_msg = {
                    cmd: "pmsg",
                    val: DATA,
                    id: String(ID)
                }

                if (this.enableListener) {
                    tmp_msg["listener"] = String(this.setListener);
                };

                console.log("TX:", tmp_msg);
                mWS.send(JSON.stringify(tmp_msg));

                if (this.enableListener) {
                    if (!self.socketListeners.hasOwnProperty(this.setListener)) {
                        self.socketListeners[this.setListener] = false;
                    };
                    self.enableListener = false;
                };
			} else {
				console.warn("Blocking attempt to send packet larger than 1000 bytes (1 KB), packet is " + String(DATA).length + " bytes");
			};
    	} else {
    		console.warn("Socket is not open.");
    	};
    };
    
    sendGDataAsVar({VAR, DATA }) {
        const self = this;
        if (this.isRunning) {
            if (!(String(DATA).length > 1000)) {
                let tmp_msg = {
                    cmd: "gvar",
                    name: VAR,
                    val: DATA
                }

                if (this.enableListener) {
                    tmp_msg["listener"] = String(this.setListener);
                };

                console.log("TX:", tmp_msg);
                mWS.send(JSON.stringify(tmp_msg));

                if (this.enableListener) {
                    if (!self.socketListeners.hasOwnProperty(this.setListener)) {
                        self.socketListeners[this.setListener] = false;
                    };
                    self.enableListener = false;
                };
            } else {
                console.warn("Blocking attempt to send packet larger than 1000 bytes (1 KB), packet is " + String(DATA).length + " bytes");
            };
        } else {
            console.warn("Socket is not open.");
        };
    };
    
    sendPDataAsVar({VAR, ID, DATA}) {
        const self = this;
        if (this.isRunning) {
            if (!(String(DATA).length > 1000)) {
                let tmp_msg = {
                    cmd: "pvar",
                    name: VAR,
                    val: DATA,
                    id: String(ID)
                }

                if (this.enableListener) {
                    tmp_msg["listener"] = String(this.setListener);
                };

                console.log("TX:", tmp_msg);
                mWS.send(JSON.stringify(tmp_msg));

                if (this.enableListener) {
                    if (!self.socketListeners.hasOwnProperty(this.setListener)) {
                        self.socketListeners[this.setListener] = false;
                    };
                    self.enableListener = false;
                };
            } else {
                console.warn("Blocking attempt to send packet larger than 1000 bytes (1 KB), packet is " + String(DATA).length + " bytes");
            };
        } else {
            console.warn("Socket is not open.");
        };
    };
    
    runCMD({CMD, ID, DATA}) {
		const self = this;
		
		let tmp_DATA = DATA;
		if (this.isValidJSON({"JSON_STRING": DATA})) {
			tmp_DATA = JSON.parse(DATA);
		};
		console.log(tmp_DATA);
		
        if (this.isRunning) {
    		if (!(String(CMD).length > 100) || !(String(ID).length > 20) || !(String(DATA).length > 1000)) {
                let tmp_msg = {
                    cmd: String(CMD),
                    id: String(ID),
                    val: tmp_DATA
                }

                if (this.enableListener) {
                    tmp_msg["listener"] = String(this.setListener);
                };

                console.log("TX:", tmp_msg);
                mWS.send(JSON.stringify(tmp_msg));
				
                if (this.enableListener) {
                    if (!self.socketListeners.hasOwnProperty(this.setListener)) {
                        self.socketListeners[this.setListener] = false;
                    };
                    self.enableListener = false;
                };
			} else {
				console.warn("Blocking attempt to send packet with questionably long arguments");
			};
    	} else {
    		console.warn("Socket is not open.");
    	};
    };
    
    resetNewData({TYPE}){
		const self = this;
        if (this.isRunning) {
			self.newSocketData[this.menuRemap[String(TYPE)]] = false;
		};
    };
    
    resetNewVarData({ TYPE, VAR }) {
        if (this.isRunning) {
            if (self.varData.hasOwnProperty(this.menuRemap[TYPE])) {
                if (self.varData[this.menuRemap[TYPE]].hasOwnProperty(VAR)) {
                    self.varData[this.menuRemap[TYPE]][VAR].isNew = false;
                };
            };
        };
    };

    resetNewListener({ ID }) {
        const self = this;
        if (this.isRunning) {
            if (this.socketListeners.hasOwnProperty(String(ID))) {
                self.socketListeners[String(ID)] = false;
            };
        };
    };

    clearAllPackets({TYPE}){
		const self = this;
		if (this.menuRemap[String(TYPE)] == "all") {
			self.socketData.gmsg = [];
			self.socketData.pmsg = [];
			self.socketData.direct = [];
			self.socketData.statuscode = [];
			self.socketData.gvar = [];
			self.socketData.pvar = [];
		} else {
			self.socketData[this.menuRemap[String(TYPE)]] = [];
		};
    };
};

(function() {
    var extensionClass = CloudLink;
    if (typeof window === "undefined" || !window.vm) {
        Scratch.extensions.register(new extensionClass());
		console.log("CloudLink 4.0 loaded. Detecting sandboxed mode, performance will suffer. Please load CloudLink in Unsandboxed mode.");
    } else {
        var extensionInstance = new extensionClass(window.vm.extensionManager.runtime);
        var serviceName = window.vm.extensionManager._registerInternalExtension(extensionInstance);
        window.vm.extensionManager._loadedExtensions.set(extensionInstance.getInfo().id, serviceName);
		console.log("CloudLink 4.0 loaded. Detecting unsandboxed mode.");
    };
})()