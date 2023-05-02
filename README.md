![CLOUDLINK 4 BANNER](https://user-images.githubusercontent.com/12957745/188282246-a221e66a-5d8a-4516-9ae2-79212b745d91.png)
##### CL4 banner(s) made by [@zedthehedgehog](https://github.com/zedthehedgehog)

# CloudLink
CloudLink is a free and open-source, websocket-powered API optimized for Scratch 3.0. CloudLink comes with several powerful utilities and features:
* Multicast and unicasting messages - Perfect for high-speed projects
* Friendly software suite for implementing project-specific features - Multi-project save files and more
* Advanced packet queuing system - Messages are handled browser-level so your Scratch code doesn't need to do extra work
* Support for sandboxed/unsandboxed extension modes
* Proven reliability - Extensively tested and utilized in [The Meower Project](https://github.com/meower-media-co/)
* Unique project identifiers to allow frictionless communication between projects and app servers over a single CloudLink Server

CloudLink is now powered by [aaugustin/websockets!](https://github.com/aaugustin/websockets) CloudLink will perform better and more reliably than before.

## Get started with CloudLink
For full documentation of CloudLink, please visit CloudLink's [Documentation](https://hackmd.io/g6BogABhT6ux1GA2oqaOXA) page.

There are several publically-hosted CloudLink instances available, which can be found in [serverlist.json](https://github.com/MikeDev101/cloudlink/blob/master/serverlist.json) or through the Server List block. 

CloudLink was originally created for Scratch 3.0. You can view the latest version of CloudLink in any of these Scratch editors:
- [TurboWarp](https://turbowarp.org/editor?extension=https://mikedev101.github.io/cloudlink/S4-0-nosuite.js)
- [SheepTester's E 羊 icques](https://sheeptester.github.io/scratch-gui/?url=https://mikedev101.github.io/cloudlink/S4-0-nosuite.js)
- [Ogadaki's Adacraft](https://adacraft.org/studio/)
- [Ogadaki's Adacraft (Beta)](https://beta.adacraft.org/studio/)

CloudLink is also available as a Python module, which comes bundled with the CloudLink Server.
There is even a web-friendly version of CloudLink available as CLJS. 

### [Discussion Forum (Archive)](https://scratch.mit.edu/discuss/topic/398473)
### [CloudLink JS "CLJS"](https://www.npmjs.com/package/@williamhorning/cloudlink)

## FAQ
> Will my CloudLink 3.0/TURBO projects support CloudLink 4.0 Servers?

Yes, there will be no compatibility-breaking changes to how CloudLink 4.0 handles messages. However, the new custom command handler will bind all custom commands to use: `{"cmd": "(custom command here)"}` instead of using the Direct command, `{"cmd": "direct", "val": {"cmd": "(custom command here)"}}`

> Will my Server (v0.1.7.x and older) need to be rewritten entirely to support CloudLink 4.0?

No, you will only need to rewrite your custom packet handlers as CloudLink 4.0 will reimplement custom commands.

> Where can I find old versions of CloudLink?

You can check the releases tab in Github for older versions, or you can download a complete archive of all old versions here (LINK TBD).

> Will CloudLink 4.0 work with my project made for CloudLink TURBO?

No, CloudLink 4.0 serves as a replacement of CloudLink TURBO. While CloudLink 4.0 is built upon CloudLink TURBO, it does not have the same blocks as CloudLink TURBO. In favor or retaining compatibility with CloudLink 3.0, CloudLink TURBO should not be used and will be retired.

> Will my older projects (prior to CloudLink 3.0) work with CloudLink 4.0?

No, only projects built with CloudLink 3.0 will work with CloudLink 4.0.

> Does CloudLink 4.0 have the CloudLink Suite?

Yes. CloudLink 4.0 will be a complete reimplementation of the original CloudLink Suite. 

> What is the CloudLink Suite?

The Cloudlink Suite is a set of extra features built into the Cloudlink Extension. It provides extra features for Scratch developers to implement in projects that would normally add extra bloat, but can be implemented in a few blocks. These features include:
* CloudDisk: Completely free cloud storage (Up to 10 KB, or 10^4 Bytes, per account), and a cross-project, cross-platform save file system (Up to 1 KB, or 10^3 Bytes, per save file with a maximum of 10 save files).
* CloudCoin: Simple per-project, per-user currency system and supports cross-project trading.
* CloudAccount: Extremely easy-to-use username/password system as an alternative to the username block for user identification, and protects your CloudCoin and CloudDisk data from unwanted users.

## Found an issue?
Please report any bugs, glitches, and/or security vulnerabilities [here](https://github.com/MikeDev101/cloudlink/issues).
