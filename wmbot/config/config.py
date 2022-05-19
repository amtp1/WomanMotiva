import os
from dataclasses import dataclass

from dotenv import load_dotenv, find_dotenv


@dataclass
class Config:
    token: str
    host: str
    port: int

    wa_email: str
    wa_password: str
    wa_app_id: str
    wa_token: str
    wa_license_id: int

    def __init__(self):
        load_dotenv(find_dotenv())
        self.set_config()

    def set_config(self):
        self.token = os.getenv("BOT_TOKEN")
        self.host = os.getenv("WEB_HOST")
        self.port = os.getenv("WEB_PORT")

        self.wa_email = os.getenv("WA_EMAIL")
        self.wa_password = os.getenv("WA_PASSWORD")
        self.wa_app_id = os.getenv("WA_APP_ID")
        self.wa_token = os.getenv("WA_TOKEN")
        self.wa_license_id = os.getenv("WA_LICENSE_ID")