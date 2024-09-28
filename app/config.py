import os
import sys

from sanic.log import logger

from dotenv import load_dotenv


def get_dotenv_path() -> str | None:
    cwd = os.getcwd()
    env_path = os.path.join(cwd, '.env')
    if os.path.exists(env_path):
        return env_path

    next_env_path = os.path.join(os.path.dirname(cwd), '.env')
    if os.path.exists(next_env_path):
        return next_env_path


def load():
    path = get_dotenv_path()
    if path is None:
        logger.critical("No .env file found. Exiting.")
        sys.exit(1)
    logger.info(f"Loading .env file from {path}")

load()