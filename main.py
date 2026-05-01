import argparse
import src
import src.config
import asyncio
import logging

logging.basicConfig(
    format="%(asctime)s %(levelname)s: %(message)s",
    level=logging.INFO,
    )

async def main():
    parser = argparse.ArgumentParser(prog="anomaly-searcher")
    parser.add_argument("-c", "--config", 
        action="store", 
        required=True,
        help="path to configuration file")
    opts = vars(parser.parse_args())

    app_conf = src.config.from_yaml(opts["config"])
    app_to_run = src.App(app_conf)

    logging.getLogger(__name__).info("app initialized")

    await app_to_run.start()


if __name__ == "__main__":
    asyncio.run(main())