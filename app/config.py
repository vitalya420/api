import os
import sys

from dotenv import load_dotenv, dotenv_values


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
        sys.exit(1)
    load_dotenv(dotenv_path=path)


class Config(dict):
    _singleton = None

    def __new__(cls, *args, **kwargs):
        if cls._singleton is None:
            cls._singleton = super().__new__(cls)
        return cls._singleton

    def __init__(self):
        super().__init__(**os.environ)
        path = get_dotenv_path()
        if path:
            self.update(dotenv_values(path))


config = Config()
