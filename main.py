from cloudlink import cloudlink


if __name__ == "__main__":
    cl = cloudlink.server()
    
    # Set logging level
    cl.logging.basicConfig(
        format="[%(asctime)s] %(levelname)s: %(message)s",
        level=cl.logging.DEBUG
    )

    # Configure
    cl.enable_motd = True
    cl.motd_message = "Hello world!"
    cl.enable_scratch_support = True
    cl.max_clients = 5 # Set to -1 for unlimited

    # Start the server
    cl.run()
