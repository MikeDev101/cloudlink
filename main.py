from cloudlink import cloudlink


if __name__ == "__main__":
    cl = cloudlink.server()

    cl.logging.basicConfig(
        format="[%(asctime)s] %(levelname)s: %(message)s",
        level=cl.logging.INFO
    )

    cl.run(port=3000)
    