import os
from dataclasses import dataclass

import dotenv
from dotenv import load_dotenv, find_dotenv


@dataclass
class Config:
    timeout_sec: int

    def __init__(self):
        load_dotenv(find_dotenv())
        self.set_config()

    def set_config(self):
        self.timeout_sec = os.getenv("TIMEOUT_SEC")

    def change_value(self, key, value):
        os.environ[key] = value
        dotenv.set_key(dotenv.find_dotenv(), key, os.environ[key])