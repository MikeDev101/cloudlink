// Name: Cloudlink
// ID: cloudlink
// Description: A powerful WebSocket extension for Scratch.
// By: MikeDEV

(function (Scratch) {

  /*
  CloudLink Scratch Extension v0.1.0 - TurboWarp, S4.0/S4.1 backward-compatible

  Server versions supported via backward compatibility:
  - 0.1.5 (internally S2.2)
  - 0.1.7
  - 0.1.8.x
  - 0.1.9.x
  - 0.2.0 (latest)

  MIT License
  Copyright 2023 Mike J. Renaker / "MikeDEV".
  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"),
  to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
  and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF 
  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
  FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
  WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
  */

  // Require extension to be unsandboxed.
  'use strict';
  if (!Scratch.extensions.unsandboxed) {
    throw new Error('The CloudLink extension must run unsandboxed.');
  }

  // Declare icons as static SVG URIs
  const cl_icon =
    "data:image/svg+xml;base64,PHN2ZyB2ZXJzaW9uPSIxLjEiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgeG1sbnM6eGxpbms9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkveGxpbmsiIHdpZHRoPSIyMjUuMzU0OCIgaGVpZ2h0PSIyMjUuMzU0OCIgdmlld0JveD0iMCwwLDIyNS4zNTQ4LDIyNS4zNTQ4Ij48ZyB0cmFuc2Zvcm09InRyYW5zbGF0ZSgtMTI3LjMyMjYsLTY3LjMyMjYpIj48ZyBkYXRhLXBhcGVyLWRhdGE9InsmcXVvdDtpc1BhaW50aW5nTGF5ZXImcXVvdDs6dHJ1ZX0iIHN0cm9rZT0ibm9uZSIgc3Ryb2tlLWxpbmVjYXA9ImJ1dHQiIHN0cm9rZS1saW5lam9pbj0ibWl0ZXIiIHN0cm9rZS1taXRlcmxpbWl0PSIxMCIgc3Ryb2tlLWRhc2hhcnJheT0iIiBzdHJva2UtZGFzaG9mZnNldD0iMCIgc3R5bGU9Im1peC1ibGVuZC1tb2RlOiBub3JtYWwiPjxwYXRoIGQ9Ik0xMjcuMzIyNiwxODBjMCwtNjIuMjMwMDEgNTAuNDQ3MzksLTExMi42Nzc0IDExMi42Nzc0LC0xMTIuNjc3NGM2Mi4yMzAwMSwwIDExMi42Nzc0LDUwLjQ0NzM5IDExMi42Nzc0LDExMi42Nzc0YzAsNjIuMjMwMDEgLTUwLjQ0NzM5LDExMi42Nzc0IC0xMTIuNjc3NCwxMTIuNjc3NGMtNjIuMjMwMDEsMCAtMTEyLjY3NzQsLTUwLjQ0NzM5IC0xMTIuNjc3NCwtMTEyLjY3NzR6IiBmaWxsPSIjMDBjMjhjIiBmaWxsLXJ1bGU9Im5vbnplcm8iIHN0cm9rZS13aWR0aD0iMCIvPjxnIGZpbGwtcnVsZT0iZXZlbm9kZCIgc3Ryb2tlLXdpZHRoPSIxIj48cGF0aCBkPSJNMjg2LjEyMDM3LDE1MC41NTc5NWMyMy4yNDA4NiwwIDQyLjA3ODksMTguODM5NDYgNDIuMDc4OSw0Mi4wNzg5YzAsMjMuMjM5NDQgLTE4LjgzODAzLDQyLjA3ODkgLTQyLjA3ODksNDIuMDc4OWgtOTIuMjQwNzRjLTIzLjI0MDg2LDAgLTQyLjA3ODksLTE4LjgzOTQ2IC00Mi4wNzg5LC00Mi4wNzg5YzAsLTIzLjIzOTQ0IDE4LjgzODAzLC00Mi4wNzg5IDQyLjA3ODksLTQyLjA3ODloNC4xODg4N2MxLjgxMTUzLC0yMS41NzA1NSAxOS44OTM1NywtMzguNTEyODkgNDEuOTMxNSwtMzguNTEyODljMjIuMDM3OTMsMCA0MC4xMTk5NywxNi45NDIzNCA0MS45MzE1LDM4LjUxMjg5eiIgZmlsbD0iI2ZmZmZmZiIvPjxwYXRoIGQ9Ik0yODkuMDg2NTUsMjEwLjM0MTE0djkuMDQ2NjdoLTI2LjkxNjYzaC05LjA0NjY3di05LjA0NjY3di01NC41MDMzOWg5LjA0NjY3djU0LjUwMzM5eiIgZmlsbD0iIzAwYzI4YyIvPjxwYXRoIGQ9Ik0yMjIuNDA5MjUsMjE5LjM4NzgxYy04LjM1MzIsMCAtMTYuMzY0MzEsLTMuMzE4MzQgLTIyLjI3MDksLTkuMjI0OTJjLTUuOTA2NjEsLTUuOTA2NTggLTkuMjI0OTEsLTEzLjkxNzY4IC05LjIyNDkxLC0yMi4yNzA4OWMwLC04LjM1MzIgMy4zMTgyOSwtMTYuMzY0MzEgOS4yMjQ5MSwtMjIuMjcwOWM1LjkwNjU5LC01LjkwNjYxIDEzLjkxNzcsLTkuMjI0OTEgMjIuMjcwOSwtOS4yMjQ5MWgyMS4xMDg5djguOTM0OThoLTIxLjEwODl2MC4xMDI1N2MtNS45NTYyOCwwIC0xMS42Njg2NCwyLjM2NjE2IC0xNS44ODAzNyw2LjU3Nzg5Yy00LjIxMTczLDQuMjExNzMgLTYuNTc3ODksOS45MjQwOCAtNi41Nzc4OSwxNS44ODAzN2MwLDUuOTU2MjggMi4zNjYxNiwxMS42Njg2NCA2LjU3Nzg5LDE1Ljg4MDM3YzQuMjExNzMsNC4yMTE3MyA5LjkyNDA4LDYuNTc3OTMgMTUuODgwMzcsNi41Nzc5M3YwLjEwMjUzaDIxLjEwODl2OC45MzQ5OHoiIGZpbGw9IiMwMGMyOGMiLz48L2c+PC9nPjwvZz48L3N2Zz48IS0tcm90YXRpb25DZW50ZXI6MTEyLjY3NzQwNDA4NDA4MzkyOjExMi42Nzc0MDQwODQwODQwMy0tPg==";
  const cl_block =
    "data:image/svg+xml;base64,PHN2ZyB2ZXJzaW9uPSIxLjEiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgeG1sbnM6eGxpbms9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkveGxpbmsiIHdpZHRoPSIxNzYuMzk4NTQiIGhlaWdodD0iMTIyLjY3MDY5IiB2aWV3Qm94PSIwLDAsMTc2LjM5ODU0LDEyMi42NzA2OSI+PGcgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoLTE1MS44MDA3MywtMTE4LjY2NDY2KSI+PGcgZGF0YS1wYXBlci1kYXRhPSJ7JnF1b3Q7aXNQYWludGluZ0xheWVyJnF1b3Q7OnRydWV9IiBmaWxsLXJ1bGU9ImV2ZW5vZGQiIHN0cm9rZT0ibm9uZSIgc3Ryb2tlLXdpZHRoPSIxIiBzdHJva2UtbGluZWNhcD0iYnV0dCIgc3Ryb2tlLWxpbmVqb2luPSJtaXRlciIgc3Ryb2tlLW1pdGVybGltaXQ9IjEwIiBzdHJva2UtZGFzaGFycmF5PSIiIHN0cm9rZS1kYXNob2Zmc2V0PSIwIiBzdHlsZT0ibWl4LWJsZW5kLW1vZGU6IG5vcm1hbCI+PGc+PHBhdGggZD0iTTI4Ni4xMjAzNywxNTcuMTc3NTVjMjMuMjQwODYsMCA0Mi4wNzg5LDE4LjgzOTQ2IDQyLjA3ODksNDIuMDc4OWMwLDIzLjIzOTQ0IC0xOC44MzgwMyw0Mi4wNzg5IC00Mi4wNzg5LDQyLjA3ODloLTkyLjI0MDc0Yy0yMy4yNDA4NiwwIC00Mi4wNzg5LC0xOC44Mzk0NiAtNDIuMDc4OSwtNDIuMDc4OWMwLC0yMy4yMzk0NCAxOC44MzgwMywtNDIuMDc4OSA0Mi4wNzg5LC00Mi4wNzg5aDQuMTg4ODdjMS44MTE1MywtMjEuNTcwNTUgMTkuODkzNTcsLTM4LjUxMjg5IDQxLjkzMTUsLTM4LjUxMjg5YzIyLjAzNzkzLDAgNDAuMTE5OTcsMTYuOTQyMzQgNDEuOTMxNSwzOC41MTI4OXoiIGZpbGw9IiNmZmZmZmYiLz48cGF0aCBkPSJNMjg5LjA4NjU1LDIxNi45NjA3NHY5LjA0NjY3aC0yNi45MTY2M2gtOS4wNDY2N3YtOS4wNDY2N3YtNTQuNTAzMzloOS4wNDY2N3Y1NC41MDMzOXoiIGZpbGw9IiMwMGMyOGMiLz48cGF0aCBkPSJNMjIyLjQwOTI1LDIyNi4wMDc0MWMtOC4zNTMyLDAgLTE2LjM2NDMxLC0zLjMxODM0IC0yMi4yNzA5LC05LjIyNDkyYy01LjkwNjYxLC01LjkwNjU4IC05LjIyNDkxLC0xMy45MTc2OCAtOS4yMjQ5MSwtMjIuMjcwODljMCwtOC4zNTMyIDMuMzE4MjksLTE2LjM2NDMxIDkuMjI0OTEsLTIyLjI3MDljNS45MDY1OSwtNS45MDY2MSAxMy45MTc3LC05LjIyNDkxIDIyLjI3MDksLTkuMjI0OTFoMjEuMTA4OXY4LjkzNDk4aC0yMS4xMDg5djAuMTAyNTdjLTUuOTU2MjgsMCAtMTEuNjY4NjQsMi4zNjYxNiAtMTUuODgwMzcsNi41Nzc4OWMtNC4yMTE3Myw0LjIxMTczIC02LjU3Nzg5LDkuOTI0MDggLTYuNTc3ODksMTUuODgwMzdjMCw1Ljk1NjI4IDIuMzY2MTYsMTEuNjY4NjQgNi41Nzc4OSwxNS44ODAzN2M0LjIxMTczLDQuMjExNzMgOS45MjQwOCw2LjU3NzkzIDE1Ljg4MDM3LDYuNTc3OTN2MC4xMDI1M2gyMS4xMDg5djguOTM0OTh6IiBmaWxsPSIjMDBjMjhjIi8+PC9nPjwvZz48L2c+PC9zdmc+PCEtLXJvdGF0aW9uQ2VudGVyOjg4LjE5OTI2OTk5OTk5OTk4OjYxLjMzNTM0NDk5OTk5OTk5LS0+";

  // Declare VM
  const vm = Scratch.vm;

  /*
  This versioning system is intended for future use with CloudLink.
  This looks scary - But don't be afraid. It's rather simple, actually.

  When the client sends the handshake request, it will provide the server with the following details:
  {
    "cmd": "handshake",
    "val": {
      "language": "Scratch",
      "version": {
        "editorType": String,
        "fullString": String,
        "versionNumber": Number
      }
    }
  }

  Why?
  A problem with previous versions of CloudLink clients/servers is that they do not implement a proper version check system.
  Starting with the Scratch Extension rewrite, this new system will be enforced.

  version.editorType - Provides info regarding the Scratch IDE this Extension variant natively supports. Intended for server-side version identification.
  version.versionNumber - Numerical version info. Increment by 1 every Semantic Versioning Patch. Intended for server-side version identification.
  version.versionString - Semantic Versioning string. Intended for source-code versioning only.
  version.compatibleVariants - A list of per-block, fully-compatible older Scratch Extension versions this extension supports.
  version.compatibleVariantsShorthand - Shortened version of version.compatibleVariants. Intended for generating version strings within the extension.

  The extension will auto-generate a version string by using getVariantVersionString().

  DO NOT MODIFY:
  * compatibleVariants
  * compatibleVariantsShorthand
  ...without modifying versionNumber, or modifying editorType!
  I intend to support multiple IDEs and they could have completely different versionNumbers or versionStrings!
  */
  const version = {
    editorType: "TurboWarp",
    versionNumber: 0,
    versionString: "0.1.0",
    compatibleVariants: ["S4.1", "S4.0", "B4.0"],
    compatibleVariantsShorthand: "S4-X"
  };

  // Store extension state
  var clVars = {

    // WebSocket object.
    socket: null,

    // gmsg.queue - An array of all currently queued gmsg values.
    // gmsg.varState - The value of the most recently received gmsg message.
    // gmsg.hasNew - Returns true if a new gmsg value has been received.
    gmsg: {
      queue: [],
      varState: "",
      hasNew: false,
    },

    // pmsg.queue - An array of all currently queued pmsg values.
    // pmsg.varState - The value of the most recently received pmsg message.
    // pmsg.hasNew - Returns true if a new pmsg value has been received.
    pmsg: {
      queue: [],
      varState: "",
      hasNew: false,
    },

    // gvar.queue - An array of all currently queued gvar values.
    // gvar.varStates - A dictionary storing each gvar variable.
    // gvar.hasNew - Returns true if a new gvar value has been received.
    gvar: {
      queue: [],
      varStates: {},
      hasNew: false,
    },

    // pvar.queue - An array of all currently queued pvar values.
    // pvar.varStates - A dictionary storing each pvar variable.
    // pvar.hasNew - Returns true if a new pvar value has been received.
    pvar: {
      queue: [],
      varStates: {},
      hasNew: false,
    },

    // direct.queue - An array of all currently queued direct values.
    // direct.varState - The value of the most recently received direct message.
    // direct.hasNew - Returns true if a new direct value has been received.
    direct: {
      queue: [],
      varState: {},
      hasNew: false,
    },

    // statuscode.queue - An array of all currently queued statuscode values.
    // statuscode.varState - The value of the most recently received statuscode message.
    // statuscode.hasNew - Returns true if a new statuscode value has been received.
    statuscode: {
      queue: [],
      varState: {},
      hasNew: false,
    },

    // ulist.varState - Stores all currently connected client objects in the server/all subscribed room(s).
    // ulist.hasNew - Returns true if a new ulist value has been received.
    ulist: {
      varState: [],
      hasNew: false,
    },

    // Message-Of-The-Day
    motd: "",

    // Client IP address
    client_ip: "",

    // Server version string
    server_version: "",

    // listeners.enablerState - Set to true when "createListener" is used.
    // listeners.enablerValue - Set to a new listener ID when "createListener" is used.
    // listeners.current - Keeps track of all current listener IDs being awaited.
    // listeners.varStates - Storage for all successfully awaited messages from specific listener IDs.
    listeners: {
      enablerState: false,
      enablerValue: "",
      current: [],
      varStates: {}
    },

    // Temporary username storage
    tempUsername: "",

    // Username storage
    myUsername: "",

    // Store user_obj messages.
    myUserObject: {},

    /* 
    linkState.status - Current state of the connection.
      0 - Ready
      1 - Connecting
      2 - Connected
      3 - Disconnected, gracefully (OK)
      4 - Disconnected, abruptly (Connection failed / dropped)
    
    linkState.isAttemptingGracefulDisconnect - Boolean used to ignore any websocket codes other than 1000 (going away) when disconnecting.

    linkstate.disconnectType - Type of disconnect that has occurred.
      0 - Safely disconnected (connected OK and gracefully disconnected)
      1 - Connection dropped (connected OK but lost connection afterwards)
      2 - Connection failed (attempted connection but did not succeed)
    
    linkstate.identifiedProtocol - Enables backwards compatibility for CL servers.
      0 - CL3 0.1.5 "S2.2" - Doesn't support listeners, MOTD, or statuscodes.
      1 - CL3 0.1.7 - Doesn't support listeners, has early MOTD support, and early statuscode support.
      2 - CL4 0.1.8.x - First version to support listeners, and modern server_version support. First version to implement rooms support.
      3 - CL4 0.1.9.x - First version to implement the handshake command and better ulist events.
      4 - CL4 0.2.0 - Latest version. First version to implement client_obj and enhanced ulists.
    */
    linkState: {
      status: 0,
      isAttemptingGracefulDisconnect: false,
      disconnectType: 0,
      identifiedProtocol: 0,
    },

    // Timeout of 500ms upon connection to try and handshake. Automatically aborted if server_version is received.
    handshakeTimeout: null,

    // Prevent accidentally sending the handshake more than once per connection.
    handshakeAttempted: false,


    // Storage for the publically available CloudLink instances.
    serverList: {},
  }

  function getVariantVersionString() {
    return `${version.editorType}_${version.versionString}_${version.compatibleVariantsShorthand}`;
  }

  // Makes values safe for Scratch to represent.
  async function makeValueScratchSafe(data) {
    if (typeof data == "object") {
      try {
        return JSON.stringify(data);
      } catch (SyntaxError) {
        return String(data);
      }
    } else {
      return String(data);
    }
  }

  // Clears out and resets the various values of clVars upon disconnect.
  function resetValuesOnClose() {
    window.clearTimeout(clVars.handshakeTimeout);
    clVars.handshakeAttempted = false;
    clVars.socket = null;
    clVars.motd = "";
    clVars.client_ip = "";
    clVars.server_version = "";
    clVars.tempUsername = "";
    clVars.myUsername = "";
    clVars.linkState.identifiedProtocol = 0;
    clVars.linkState.isAttemptingGracefulDisconnect = false;
    clVars.myUserObject = {};
    clVars.gmsg = {
      queue: [],
      varState: "",
      hasNew: false,
    };
    clVars.pmsg = {
      queue: [],
      varState: "",
      hasNew: false,
    };
    clVars.gvar = {
      queue: [],
      varStates: {},
      hasNew: false,
    };
    clVars.pvar = {
      queue: [],
      varStates: {},
      hasNew: false,
    };
    clVars.direct = {
      queue: [],
      varState: {},
      hasNew: false,
    };
    clVars.statuscode = {
      queue: [],
      varState: {},
      hasNew: false,
    };
    clVars.ulist = {
      varState: [],
      hasNew: false,
    };
    clVars.listeners = {
      enablerState: false,
      enablerValue: "",
      current: [],
      varStates: {}
    };
  }

  // CL-specific netcode needed for sending messages
  async function sendCloudLinkMessage(message) {
    // Prevent running this while disconnected
    if (clVars.socket == null) {
      console.warn("[CloudLink] Ignoring attempt to send a packet while disconnected.");
      return;
    }

    // See if the outgoing val argument can be converted into JSON
    if (message.hasOwnProperty("val")) {
      try {
        message.val = JSON.parse(message.val);
      } catch { }
    }

    // Attach listeners
    if (clVars.listeners.enablerState) {

      // 0.1.8.x was the first server version to support listeners.
      if (clVars.linkState.identifiedProtocol >= 2) {
        message.listener = clVars.listeners.enablerValue;
      } else {
        console.warn("[CloudLink] Server is too old! Must be at least 0.1.8.x to support listeners.");
      }
      clVars.listeners.enablerState = false;
    }

    // Check if server supports rooms
    if (((message.cmd == "link") || (message.cmd == "unlink")) && (clVars.linkState.identifiedProtocol < 2)) {
      // 0.1.8.x was the first server version to support rooms.
      console.warn("[CloudLink] Server is too old! Must be at least 0.1.8.x to support room linking/unlinking.");
      return;
    }

    // Convert the outgoing message to JSON
    let outgoing = "";
    try {
      outgoing = JSON.stringify(message);
    } catch (SyntaxError) {
      console.warn("[CloudLink] Failed to send a packet, invalid syntax:", message);
      return;
    }

    // Send the message
    console.log("[CloudLink] TX:", message);
    clVars.socket.send(outgoing);
  }

  function sendHandshake() {
    if (clVars.handshakeAttempted) return;
    console.log("[CloudLink] Sending handshake...");
    sendCloudLinkMessage({
      cmd: "handshake",
      val: {
        language: "Scratch",
        version: {
          fullString: getVariantVersionString(),
          editorType: version.editorType,
          versionNumber: version.versionNumber,
        },
      },
      listener: "handshake_cfg"
    });
    clVars.handshakeAttempted = true;
  }

  // Compare the version string of the server to known compatible variants to configure clVars.linkState.identifiedProtocol.
  function setServerVersion(version) {
    console.log(`[CloudLink] Server version: ${String(version)}`);
    clVars.server_version = version;

    // Auto-detect versions
    const versions = {
      "0.2.": 4,
      "0.1.9": 3,
      "0.1.8": 2,
      "0.1.7": 1,
      "S2.2": 0, // 0.1.5
      "0.1.": 0, // 0.1.5 or legacy
      "S2.": 0, // Legacy
      "S1.": -1 // Obsolete
    };

    Object.entries(versions).forEach(([key, value]) => {
      if (String(version).toLowerCase().includes(key)) {
        if (clVars.linkState.identifiedProtocol < value) {

          // Disconnect if protcol is too old
          if (value == -1) {
            console.warn(`[CloudLink] Server is too old to enable leagacy support. Disconnecting.`);
            return clVars.socket.close(1000, "");
          }
          
          // Set the identified protocol variant
          console.log(`[CloudLink] Configuring identified protocol variant to v${value}.`);
          clVars.linkState.identifiedProtocol = value;

          // Display warning messages depending upon features supported by the server.
          switch (value) {
            case 3:
              console.warn("[CloudLink] Enabling legacy support. Some features may be modified, but they should continue to function as intended. It is recommended to upgrade your server.");
              break;
            case 2:
              console.warn("[CloudLink] Enabling legacy support. Some features may be modified, but they should continue to function as intended. It is recommended to upgrade your server.");
              break;
            case 1:
              console.warn("[CloudLink] Enabling legacy support. Listeners and rooms will be disabled. It is recommended to upgrade your server.");
              break;
            case 0:
              console.warn("[CloudLink] Enabling legacy support. Listeners and rooms will be disabled. It is recommended to upgrade your server.");
              break;
          }
        }
      }
    });

    // Send handshake command (if server supports it)
    if (clVars.linkState.identifiedProtocol < 3) return;
    sendHandshake();
  }

  // CL-specific netcode needed to make the extension work
  async function messageHandlerCloudLinkClient(data) {
    // Parse the message JSON
    let packet = {};
    try {
      packet = JSON.parse(data)
    } catch (SyntaxError) {
      console.error("[CloudLink] Incoming message parse failure! Is this really a CloudLink server?", data);
      return;
    };

    // Handle packet commands
    if (!packet.hasOwnProperty("cmd")) {
      console.error("[CloudLink] Incoming message read failure! This message doesn't contain the required \"cmd\" key. Is this really a CloudLink server?", packet);
      return;
    }
    console.log("[CloudLink] RX:", packet);
    switch (packet.cmd) {
      case "gmsg":
        clVars.gmsg.varState = packet.val;
        clVars.gmsg.hasNew = true;
        clVars.gmsg.queue.push(packet);
        break;

      case "pmsg":
        clVars.pmsg.varState = packet.val;
        clVars.pmsg.hasNew = true;
        clVars.pmsg.queue.push(packet);
        break;

      case "gvar":
        clVars.gvar.varStates[packet.name] = packet.val;
        clVars.gvar.hasNew = true;
        clVars.gvar.queue.push(packet);
        break;

      case "pvar":
        clVars.pvar.varStates[packet.name] = packet.val;
        clVars.pvar.hasNew = true;
        clVars.pvar.queue.push(packet);
        break;

      case "direct":
        // Handle events from older server versions
        if (packet.val.hasOwnProperty("cmd")) {
          switch (packet.val.cmd) {
            // Server 0.1.5 (at least)
            case "vers":
              window.clearTimeout(clVars.handshakeTimeout);
              setServerVersion(packet.val.val);
              return;

            // Server 0.1.7 (at least)
            case "motd":
              console.log("[CloudLink] Message of the day:", packet.val.val);
              clVars.motd = packet.val.val;
              return;
          }
        }

        // Store direct value
        clVars.direct.varState = packet.val;
        clVars.direct.hasNew = true;
        clVars.direct.queue.push(packet);
        break;

      case "client_obj":
        clVars.myUserObject = packet.val;
        break;

      case "statuscode":
        // TODO: finish statuscode handling

        // Detect older versions
        if (packet.hasOwnProperty("val")) {

        }

        break;

      case "ulist":


        break;

      case "server_version":
        window.clearTimeout(clVars.handshakeTimeout);
        setServerVersion(packet.val);
        break;

      case "client_ip":
        console.log("[CloudLink] Client IP address:", packet.val);
        clVars.client_ip = packet.val;
        break;

      case "motd":
        console.log("[CloudLink] Message of the day:", packet.val);
        clVars.motd = packet.val;
        break;

      default:
        console.warn("[CloudLink] Unrecognised incoming command:", packet.cmd);
        return;
    };

    // Handle listeners
    if (!packet.hasOwnProperty("listener")) return;

    // Check if the listener is internal to the extension. TODO: Finish this
    switch (packet.listener) {
      case "handshake_cfg":
        // The handshake request has been returned.
        break;

      case "username_cfg":
        // The set username request has been returned.
        break;
    }
  }

  // Basic netcode needed to make the extension work
  async function newCloudLinkClient(url) {
    if (!(await Scratch.canFetch(url))) {
      console.warn("[CloudLink] Did not get permission to connect, aborting.");
      return;
    }

    // Set the link state to connecting
    clVars.linkState.status = 1;
    clVars.linkState.disconnectType = 0;

    // Establish a connection to the server
    console.log("[CloudLink] Connecting to server:", url);
    try {
      clVars.socket = new WebSocket(url);
    } catch (e) {
      console.warn("[CloudLink]] An exception has occurred:", e);
      return;
    }

    // Bind connection established event
    clVars.socket.onopen = function (event) {
      
      // Set the link state to connected.
      console.log("[CloudLink] Connected.");
      clVars.linkState.status = 2;
      vm.runtime.startHats('cloudlink_onConnect');

      // If a server_version message hasn't been received in over half a second, try to broadcast a handshake
      clVars.handshakeTimeout = window.setTimeout(function() {
        console.log("[CloudLink]` Hmm... This server hasn't sent us it's server info. Going to attempt a handshake.");
        sendHandshake();
      }, 500);

      // Return promise (during setup)
      return;
    };

    // Bind message handler event
    clVars.socket.onmessage = function (event) {
      messageHandlerCloudLinkClient(event.data);
    };

    // Bind connection closed event
    clVars.socket.onclose = function (event) {
      switch (clVars.linkState.status) {
        case 1: // Was connecting
          // Set the link state to ungraceful disconnect.
          console.log(`[CloudLink] Connection failed (${event.code}).`);
          clVars.linkState.status = 4;
          clVars.linkState.disconnectType = 1;
          break;

        case 2: // Was already connected
          if (event.wasClean || clVars.linkState.isAttemptingGracefulDisconnect) {
            // Set the link state to graceful disconnect.
            console.log(`[CloudLink] Disconnected (${event.code} ${event.reason}).`);
            clVars.linkState.status = 3;
            clVars.linkState.disconnectType = 0;
          } else {
            // Set the link state to ungraceful disconnect.
            console.log(`[CloudLink] Lost connection (${event.code} ${event.reason}).`);
            clVars.linkState.status = 4;
            clVars.linkState.disconnectType = 2;
          }
          break;
      }

      // Reset clVars values
      resetValuesOnClose();

      // Run all onClose event blocks
      vm.runtime.startHats('cloudlink_onClose');
      // Return promise (during setup)
      return;
    }
  }

  // GET the serverList
  try {
    Scratch.fetch(
      "https://mikedev101.github.io/cloudlink/serverlist.json"
    )
      .then((response) => {
        return response.text();
      })
      .then((data) => {
        clVars.serverList = JSON.parse(data);
      })
      .catch((err) => {
        console.log("[CloudLink] An error has occurred while parsing the public server list:", err);
        clVars.serverList = {};
      });
  } catch (err) {
    console.log("[CloudLink] An error has occurred while fetching the public server list:", err);
    clVars.serverList = {};
  }

  // Declare the CloudLink library.
  class CloudLink {
    getInfo() {
      return {
        id: 'cloudlink',
        name: 'CloudLink',
        blockIconURI: cl_block,
        menuIconURI: cl_icon,
        docsURI: "https://github.com/MikeDev101/cloudlink/wiki/Scratch-Client",
        blocks: [

          {
            opcode: "returnGlobalData",
            blockType: Scratch.BlockType.REPORTER,
            text: "Global data"
          },

          {
            opcode: "returnPrivateData",
            blockType: Scratch.BlockType.REPORTER,
            text: "Private data"
          },

          {
            opcode: "returnDirectData",
            blockType: Scratch.BlockType.REPORTER,
            text: "Direct data"
          },

          {
            opcode: "returnLinkData",
            blockType: Scratch.BlockType.REPORTER,
            text: "Link status"
          },

          {
            opcode: "returnStatusCode",
            blockType: Scratch.BlockType.REPORTER,
            text: "Status code"
          },

          {
            opcode: "returnUserListData",
            blockType: Scratch.BlockType.REPORTER,
            text: "Usernames"
          },

          {
            opcode: "returnUsernameData",
            blockType: Scratch.BlockType.REPORTER,
            text: "My username"
          },

          {
            opcode: "returnVersionData",
            blockType: Scratch.BlockType.REPORTER,
            text: "Extension version"
          },

          {
            opcode: "returnServerVersion",
            blockType: Scratch.BlockType.REPORTER,
            text: "Server version"
          },

          {
            opcode: "returnServerList",
            blockType: Scratch.BlockType.REPORTER,
            text: "Server list"
          },

          {
            opcode: "returnMOTD",
            blockType: Scratch.BlockType.REPORTER,
            text: "Server MOTD"
          },

          {
            opcode: "returnClientIP",
            blockType: Scratch.BlockType.REPORTER,
            text: "My IP address"
          },

          {
            opcode: "returnUserObject",
            blockType: Scratch.BlockType.REPORTER,
            text: "My user object"
          },

          {
            opcode: "returnListenerData",
            blockType: Scratch.BlockType.REPORTER,
            text: "Response for listener [ID]",
            arguments: {
              ID: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: "example-listener",
              },
            },
          },

          {
            opcode: "readQueueSize",
            blockType: Scratch.BlockType.REPORTER,
            text: "Size of queue for [TYPE]",
            arguments: {
              TYPE: {
                type: Scratch.ArgumentType.STRING,
                menu: "allmenu",
                defaultValue: "All data",
              },
            },
          },

          {
            opcode: "readQueueData",
            blockType: Scratch.BlockType.REPORTER,
            text: "Packet queue for [TYPE]",
            arguments: {
              TYPE: {
                type: Scratch.ArgumentType.STRING,
                menu: "allmenu",
                defaultValue: "All data",
              },
            },
          },

          {
            opcode: "returnVarData",
            blockType: Scratch.BlockType.REPORTER,
            text: "[TYPE] [VAR] data",
            arguments: {
              VAR: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: "Apple",
              },
              TYPE: {
                type: Scratch.ArgumentType.STRING,
                menu: "varmenu",
                defaultValue: "Global variables",
              },
            },
          },

          {
            opcode: "parseJSON",
            blockType: Scratch.BlockType.REPORTER,
            text: "[PATH] of [JSON_STRING]",
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
          },

          {
            opcode: "getFromJSONArray",
            blockType: Scratch.BlockType.REPORTER,
            text: 'Get [NUM] from JSON array [ARRAY]',
            arguments: {
              NUM: {
                type: Scratch.ArgumentType.NUMBER,
                defaultValue: 0,
              },
              ARRAY: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: '["foo","bar"]',
              }
            }
          },

          {
            opcode: "fetchURL",
            blockType: Scratch.BlockType.REPORTER,
            text: "Fetch data from URL [url]",
            arguments: {
              url: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: "https://extensions.turbowarp.org/hello.txt",
              },
            },
          },

          {
            opcode: "requestURL",
            blockType: Scratch.BlockType.REPORTER,
            text: "Send request with method [method] for URL [url] with data [data] and headers [headers]",
            arguments: {
              method: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: "GET",
              },
              url: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: "https://extensions.turbowarp.org/hello.txt",
              },
              data: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: "{}",
              },
              headers: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: "{}",
              },
            },
          },

          {
            opcode: "makeJSON",
            blockType: Scratch.BlockType.REPORTER,
            text: "Convert [toBeJSONified] to JSON",
            arguments: {
              toBeJSONified: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: '{"test": true}',
              },
            },
          },

          {
            opcode: "onConnect",
            blockType: Scratch.BlockType.EVENT,
            text: "When connected",
            isEdgeActivated: false,
            shouldRestartExistingThreads: true,
          },

          {
            opcode: "onClose",
            blockType: Scratch.BlockType.EVENT,
            text: "When disconnected",
            isEdgeActivated: false,
            shouldRestartExistingThreads: true,
          },

          {
            opcode: "onListener",
            blockType: Scratch.BlockType.EVENT,
            text: "When I receive new message with listener [ID]",
            isEdgeActivated: false,
            shouldRestartExistingThreads: true,
            arguments: {
              ID: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: "example-listener",
              },
            },
          },

          {
            opcode: "onNewPacket",
            blockType: Scratch.BlockType.EVENT,
            text: "When I receive new [TYPE] message",
            isEdgeActivated: false,
            shouldRestartExistingThreads: true,
            arguments: {
              TYPE: {
                type: Scratch.ArgumentType.STRING,
                menu: "almostallmenu",
                defaultValue: "Global data",
              },
            },
          },

          {
            opcode: "onNewVar",
            blockType: Scratch.BlockType.EVENT,
            text: "When I receive new [TYPE] data for [VAR]",
            isEdgeActivated: false,
            shouldRestartExistingThreads: true,
            arguments: {
              TYPE: {
                type: Scratch.ArgumentType.STRING,
                menu: "varmenu",
                defaultValue: "Global variables",
              },
              VAR: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: "Apple",
              },
            },
          },

          {
            opcode: "getComState",
            blockType: Scratch.BlockType.BOOLEAN,
            text: "Connected?",
          },

          {
            opcode: "getRoomState",
            blockType: Scratch.BlockType.BOOLEAN,
            text: "Linked to rooms?",
          },

          {
            opcode: "getComLostConnectionState",
            blockType: Scratch.BlockType.BOOLEAN,
            text: "Lost connection?",
          },

          {
            opcode: "getComFailedConnectionState",
            blockType: Scratch.BlockType.BOOLEAN,
            text: "Failed to connnect?",
          },

          {
            opcode: "getUsernameState",
            blockType: Scratch.BlockType.BOOLEAN,
            text: "Username synced?",
          },

          {
            opcode: "returnIsNewData",
            blockType: Scratch.BlockType.BOOLEAN,
            text: "Got New [TYPE]?",
            arguments: {
              TYPE: {
                type: Scratch.ArgumentType.STRING,
                menu: "datamenu",
                defaultValue: "Global data",
              },
            },
          },

          {
            opcode: "returnIsNewVarData",
            blockType: Scratch.BlockType.BOOLEAN,
            text: "Got New [TYPE] data for variable [VAR]?",
            arguments: {
              TYPE: {
                type: Scratch.ArgumentType.STRING,
                menu: "varmenu",
                defaultValue: 'Global variables',
              },
              VAR: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: "Apple",
              },
            },
          },

          {
            opcode: "returnIsNewListener",
            blockType: Scratch.BlockType.BOOLEAN,
            text: "Got new packet with listener [ID]?",
            arguments: {
              ID: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: "example-listener",
              },
            },
          },

          {
            opcode: "checkForID",
            blockType: Scratch.BlockType.BOOLEAN,
            text: "ID [ID] connected?",
            arguments: {
              ID: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: "Another name",
              },
            },
          },

          {
            opcode: "isValidJSON",
            blockType: Scratch.BlockType.BOOLEAN,
            text: "Is [JSON_STRING] valid JSON?",
            arguments: {
              JSON_STRING: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: '{"fruit": {"apples": 2, "bananas": 3}, "total_fruit": 5}',
              },
            },
          },

          {
            opcode: "openSocket",
            blockType: Scratch.BlockType.COMMAND,
            text: "Connect to [IP]",
            arguments: {
              IP: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: "ws://127.0.0.1:3000/",
              }
            }
          },

          {
            opcode: "openSocketPublicServers",
            blockType: Scratch.BlockType.COMMAND,
            text: "Connect to server [ID]",
            arguments: {
              ID: {
                type: Scratch.ArgumentType.NUMBER,
                defaultValue: 1,
              }
            }
          },

          {
            opcode: "closeSocket",
            blockType: Scratch.BlockType.COMMAND,
            text: "Disconnect"
          },

          {
            opcode: "setMyName",
            blockType: Scratch.BlockType.COMMAND,
            text: "Set [NAME] as username",
            arguments: {
              NAME: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: "A name",
              },
            },
          },

          {
            opcode: "createListener",
            blockType: Scratch.BlockType.COMMAND,
            text: "Attach listener [ID] to next packet",
            arguments: {
              ID: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: "example-listener",
              },
            },

          },

          {
            opcode: 'linkToRooms',
            blockType: Scratch.BlockType.COMMAND,
            text: "Link to room(s) [ROOMS]",
            arguments: {
              ROOMS: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: '["test"]',
              },
            }
          },

          {
            opcode: "selectRoomsInNextPacket",
            blockType: Scratch.BlockType.COMMAND,
            text: "Select room(s) [ROOMS] for next packet",
            arguments: {
              ROOMS: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: '["test"]',
              },
            },
          },

          {
            opcode: "unlinkFromRooms",
            blockType: Scratch.BlockType.COMMAND,
            text: "Unlink from all rooms",
          },

          {
            opcode: "sendGData",
            blockType: Scratch.BlockType.COMMAND,
            text: "Send [DATA]",
            arguments: {
              DATA: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: "Apple",
              },
            },
          },

          {
            opcode: "sendPData",
            blockType: Scratch.BlockType.COMMAND,
            text: "Send [DATA] to [ID]",
            arguments: {
              DATA: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: "Apple",
              },
              ID: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: "Another name",
              },
            },
          },

          {
            opcode: "sendGDataAsVar",
            blockType: Scratch.BlockType.COMMAND,
            text: "Send variable [VAR] with data [DATA]",
            arguments: {
              DATA: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: "Banana",
              },
              VAR: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: "Apple",
              },
            },
          },

          {
            opcode: "sendPDataAsVar",
            blockType: Scratch.BlockType.COMMAND,
            text: "Send variable [VAR] to [ID] with data [DATA]",
            arguments: {
              DATA: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: "Banana",
              },
              ID: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: "Another name",
              },
              VAR: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: "Apple",
              },
            },
          },
          {
            opcode: "runCMDnoID",
            blockType: Scratch.BlockType.COMMAND,
            text: "Send command without ID [CMD] [DATA]",
            arguments: {
              CMD: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: "direct",
              },
              DATA: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: "val",
              },
            },
          },
          {
            opcode: "runCMD",
            blockType: Scratch.BlockType.COMMAND,
            text: "Send command [CMD] [ID] [DATA]",
            arguments: {
              CMD: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: "direct",
              },
              ID: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: "id",
              },
              DATA: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: "val",
              },
            },
          },
          {
            opcode: "resetNewData",
            blockType: Scratch.BlockType.COMMAND,
            text: "Reset got new [TYPE] status",
            arguments: {
              TYPE: {
                type: Scratch.ArgumentType.STRING,
                menu: "datamenu",
                defaultValue: "Global data",
              },
            },
          },
          {
            opcode: "resetNewVarData",
            blockType: Scratch.BlockType.COMMAND,
            text: "Reset got new [TYPE] [VAR] status",
            arguments: {
              TYPE: {
                type: Scratch.ArgumentType.STRING,
                menu: "varmenu",
                defaultValue: "Global variables",
              },
              VAR: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: "Apple",
              },
            },
          },
          {
            opcode: "resetNewListener",
            blockType: Scratch.BlockType.COMMAND,
            text: "Reset got new [ID] listener status",
            arguments: {
              ID: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: "example-listener",
              },
            },
          },
          {
            opcode: "clearAllPackets",
            blockType: Scratch.BlockType.COMMAND,
            text: "Clear all packets for [TYPE]",
            arguments: {
              TYPE: {
                type: Scratch.ArgumentType.STRING,
                menu: "allmenu",
                defaultValue: "All data",
              },
            }
          }
        ],
        menus: {
          coms: {
            items: ["Connected", "Username synced"]
          },
          datamenu: {
            items: ['Global data', 'Private data', 'Direct data', 'Status code']
          },
          varmenu: {
            items: ['Global variables', 'Private variables']
          },
          allmenu: {
            items: ['Global data', 'Private data', 'Direct data', 'Status code', "Global variables", "Private variables", "All data"]
          },
          almostallmenu: {
            items: ['Global data', 'Private data', 'Direct data', 'Status code', "Global variables", "Private variables"]
          },
        }
      };
    }

    // Reporter - Returns gmsg values.
    returnGlobalData() {
      return makeValueScratchSafe(clVars.gmsg.varState);
    }

    // Reporter - Returns pmsg values.
    returnPrivateData() {
      return makeValueScratchSafe(clVars.pmsg.varState);
    }

    // Reporter - Returns direct values.
    returnDirectData() {
      return makeValueScratchSafe(clVars.direct.varState);
    }

    // Reporter - Returns current link state.
    returnLinkData() {
      return makeValueScratchSafe(clVars.linkState.status);
    }

    // Reporer - Returns status code values.
    returnStatusCode() {
      return makeValueScratchSafe(clVars.statuscode.varState);
    }

    // Reporter - Returns ulist value.
    returnUserListData() {
      return makeValueScratchSafe(clVars.ulist.varState);
    }

    // Reporter - Returns currently set username.
    returnUsernameData() {
      return makeValueScratchSafe(clVars.myUsername);
    }

    // Reporter - Returns current client version.
    returnVersionData() {
      return getVariantVersionString();
    }

    // Reporter - Returns reported server version.
    returnServerVersion() {
      return makeValueScratchSafe(clVars.server_version);
    }

    // Reporter - Returns the serverlist value.
    returnServerList() {
      return makeValueScratchSafe(clVars.serverList);
    }

    // Reporter - Returns the reported Message-Of-The-Day.
    returnMOTD() {
      return makeValueScratchSafe(clVars.motd);
    }

    // Reporter - Returns the reported IP address of the client.
    returnClientIP() {
      return makeValueScratchSafe(clVars.client_ip);
    }

    // Reporter - Returns the reported user object of the client (Snowflake ID, UUID, Username)
    returnUserObject() {
      return makeValueScratchSafe(clVars.myUserObject);
    }

    // Reporter - Returns data for a specific listener ID.
    // ID - String (listener ID)
    returnListenerData(args) { } // TODO: Finish this

    // Reporter - Returns the size of the message queue.
    // TYPE - String (menu allmenu)
    readQueueSize(args) { } // TODO: Finish this

    // Reporter - Returns all values of the message queue.
    // TYPE - String (menu allmenu)
    readQueueData(args) { } // TODO: Finish this

    // Reporter - Returns a gvar/pvar value.
    // TYPE - String (menu varmenu), VAR - String (variable name)
    returnVarData(args) { } // TODO: Finish this

    // Reporter - Gets a JSON key value from a JSON string.
    // PATH - String, JSON_STRING - String
    parseJSON(args) { } // TODO: Finish this

    // Reporter - Returns an entry from a JSON array (0-based).
    // NUM - Number, ARRAY - String (JSON Array)
    getFromJSONArray(args) { } // TODO: Finish this

    // Reporter - Returns a RESTful GET promise.
    // url - String
    fetchURL(args) { } // TODO: Finish this

    // Reporter - Returns a RESTful request promise.
    // url - String, method - String, data - String, headers - String
    requestURL(args) { } // TODO: Finish this

    // Reporter - Returns a JSON-ified value.
    // toBeJSONified - String
    makeJSON(args) { } // TODO: Finish this

    // Boolean - Returns true if connected.
    getComState() {
      return ((clVars.linkState.status == 2) && (clVars.socket != null));
    }

    // Boolean - Returns true if linked to rooms (other than "default")
    getRoomState() { } // TODO: Finish this

    // Boolean - Returns true if the connection was dropped.
    getComLostConnectionState() {
      return ((clVars.linkState.status == 4) && (clVars.linkState.disconnectType == 2));
    }

    // Boolean - Returns true if the client failed to establish a connection.
    getComFailedConnectionState() {
      return ((clVars.linkState.status == 4) && (clVars.linkState.disconnectType == 1));
    }

    // Boolean - Returns true if the username was set successfully.
    getUsernameState() { } // TODO: Finish this

    // Boolean - Returns true if there is new gmsg/pmsg/direct/statuscode data.
    // TYPE - String (menu datamenu)
    returnIsNewData(args) { } // TODO: Finish this

    // Boolean - Returns true if there is new gvar/pvar data.
    // TYPE - String (menu varmenu), VAR - String (variable name)
    returnIsNewVarData(args) { } // TODO: Finish this

    // Boolean - Returns true if a listener has a new value.
    // ID - String (listener ID)
    returnIsNewListener(args) { } // TODO: Finish this

    // Boolean - Returns true if a username/ID/UUID/object exists in the userlist.
    // ID - String (username or user object)
    checkForID(args) { } // TODO: Finish this

    // Boolean - Returns true if the input JSON is valid.
    // JSON_STRING - String
    isValidJSON(args) { } // TODO: Finish this

    // Command - Establishes a connection to a server.
    // IP - String (websocket URL)
    openSocket(args) {
      if (clVars.socket != null) {
        console.warn("[CloudLink] Already connected to a server.");
        return;
      };
      return newCloudLinkClient(args.IP);
    }

    // Command - Establishes a connection to a selected server.
    // ID - Number (server entry #)
    openSocketPublicServers(args) {
      if (clVars.socket != null) {
        console.warn("[CloudLink] Already connected to a server.");
        return;
      };
      if (!clVars.serverList.hasOwnProperty(String(args.ID))) {
        console.warn("[CloudLink] Not a valid server ID!");
        return;
      };
      return newCloudLinkClient(clVars.serverList[String(args.ID)]["url"]);
    }

    // Command - Closes the connection.
    closeSocket() {
      if (clVars.socket == null) {
        console.warn("[CloudLink] Already disconnected.");
        return;
      };
      console.log("[CloudLink] Disconnecting...");
      clVars.linkState.isAttemptingGracefulDisconnect = true;
      clVars.socket.close(1000, "Client going away");
    }

    // Command - Sets the username of the client on the server.
    // NAME - String
    setMyName(args) {
      return sendCloudLinkMessage({ cmd: "setid", val: args.DATA });
    }

    // Command - Prepares the next transmitted message to have a listener ID attached to it.
    // ID - String (listener ID)
    createListener(args) {
      if (clVars.listeners.enablerState) {
        console.warn("[CloudLink] Cannot create multiple listeners at a time!");
        return;
      }
      clVars.listeners.enablerState = true;
      clVars.listeners.enablerValue = args.ID;
    }

    // Command - Subscribes to various rooms on a server.
    // ROOMS - String (JSON Array or single string)
    linkToRooms(args) { } // TODO: Finish this

    // Command - Specifies specific subscribed rooms to transmit messages to.
    // ROOMS - String (JSON Array or single string)
    selectRoomsInNextPacket(args) { } // TODO: Finish this

    // Command - Unsubscribes from all rooms and re-subscribes to the the "default" room on the server.
    unlinkFromRooms() { } // TODO: Finish this

    // Command - Sends a gmsg value.
    // DATA - String
    sendGData(args) {
      return sendCloudLinkMessage({ cmd: "gmsg", val: args.DATA });
    }

    // Command - Sends a pmsg value.
    // DATA - String, ID - String (recipient ID)
    sendPData(args) {
      return sendCloudLinkMessage({ cmd: "pmsg", val: args.DATA, id: args.ID });
    }

    // Command - Sends a gvar value.
    // DATA - String, VAR - String (variable name)
    sendGDataAsVar(args) {
      return sendCloudLinkMessage({ cmd: "gvar", val: args.DATA, name: args.VAR });
    }

    // Command - Sends a pvar value.
    // DATA - String, VAR - String (variable name), ID - String (recipient ID)
    sendPDataAsVar(args) {
      return sendCloudLinkMessage({ cmd: "pvar", val: args.DATA, name: args.VAR, id: args.ID });
    }

    // Command - Sends a raw-format command without specifying an ID.
    // CMD - String (command), DATA - String
    runCMDnoID(args) {
      return sendCloudLinkMessage({ cmd: args.CMD, val: args.DATA });
    }

    // Command - Sends a raw-format command with an ID.
    // CMD - String (command), DATA - String, ID - String (recipient ID)
    runCMD(args) {
      return sendCloudLinkMessage({ cmd: args.CMD, val: args.DATA, ID: args.ID });
    }

    // Command - Resets the "returnIsNewData" boolean state.
    // TYPE - String (menu datamenu)
    resetNewData(args) { } // TODO: Finish this

    // Command - Resets the "returnIsNewVarData" boolean state.
    // TYPE - String (menu datamenu), VAR - String (variable name)
    resetNewVarData(args) { } // TODO: Finish this

    // Command - Resets the "returnIsNewListener" boolean state.
    // ID - Listener ID
    resetNewListener(args) { } // TODO: Finish this

    // Command - Clears all packet queues.
    // TYPE - String (menu allmenu)
    clearAllPackets(args) { } // TODO: Finish this
  }
  Scratch.extensions.register(new CloudLink());
})(Scratch);