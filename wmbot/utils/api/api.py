from email import message
import json
from loguru import logger

import requests

from config.config import Config

config = Config()  # Initialize config object.


class API:
    def __init__(self):
        self.host = config.host  # Set config host from server.
        self.port = config.port  # Set config port from server.
        self.headers = {'Content-Type': 'application/json',
                        'Accept': 'application/json'}

    def get_surgeons(self, city: str) -> list:
        response = self._make_surgeons_request(
            host=self.host, port=self.port, city=city)
        content = self.serialize_response_content(content=response.text)
        return content["surgeons"]

    def create_deal(self,
                    surgeon_id: int, user_id: int, phone: str, address: str,
                    fio: str, email: str, cons_format: str, start_session, end_session
                    ) -> dict:
        response = self._make_create_deal_request(host=self.host, port=self.port, surgeon_id=surgeon_id,
                                                  user_id=user_id, phone=phone, address=address, fio=fio, email=email,
                                                  cons_format=cons_format, start_session=start_session, end_session=end_session)
        content = self.serialize_response_content(content=response.text)
        return content

    def change_status(self, deal_id: int, status: str) -> dict:
        response = self._make_change_status_request(
            host=self.host, port=self.port, deal_id=deal_id, status=status)
        content = self.serialize_response_content(content=response.content)
        return content

    def change_notice_status(self, deal_id: int) -> dict:
        response = self._make_change_notice_status_request(
            host=self.host, port=self.port, deal_id=deal_id)
        content = self.serialize_response_content(content=response.content)
        return content

    def change_qrcode_notice_status(self, deal_id: int) -> dict:
        response = self._make_change_qrcode_notice_status_request(
            host=self.host, port=self.port, deal_id=deal_id)
        content = self.serialize_response_content(content=response.content)
        return content

    def get_cities(self) -> dict:
        response = self._make_get_cities_request(
            host=self.host, port=self.port)
        content = self.serialize_response_content(content=response.content)
        return content

    def get_questions(self) -> dict:
        response = self._make_get_questions_request(
            host=self.host, port=self.port)
        content = self.serialize_response_content(content=response.content)
        return content

    def get_notices(self) -> dict:
        response = self._make_get_notices_request(
            host=self.host, port=self.port)
        content = self.serialize_response_content(content=response.content)
        return content

    def get_qrcode_notices(self) -> dict:
        response = self._make_get_qrcode_notices_request(
            host=self.host, port=self.port)
        content = self.serialize_response_content(content=response.content)
        return content

    def cancel_deal(self, deal_id: int) -> dict:
        response = self._make_cancel_deal_request(
            host=self.host, port=self.port, deal_id=deal_id)
        content = self.serialize_response_content(content=response.content)
        return content

    def _make_create_deal_request(self, **kwargs) -> requests.Response:
        url = (r"http://{host}:{port}/api/create_deal/{surgeon_id}/{user_id}/{phone}/{address}/{fio}/{email}/{cons_format}/{start_session}/{end_session}").format(**kwargs)
        response = requests.get(url=url, headers=self.headers)
        return response

    def _make_surgeons_request(self, **kwargs) -> requests.Response:
        url = r"http://{host}:{port}/api/surgeons/{city}".format(**kwargs)
        response = requests.get(url=url, headers=self.headers)
        return response

    def _make_change_status_request(self, **kwargs) -> requests.Response:
        url = r"http://{host}:{port}/api/change_status/{deal_id}/{status}".format(
            **kwargs)
        response = requests.get(url=url, headers=self.headers)
        return response

    def _make_change_notice_status_request(self, **kwargs) -> requests.Response:
        url = r"http://{host}:{port}/api/change_notice_status/{deal_id}".format(
            **kwargs)
        response = requests.get(url=url, headers=self.headers)
        return response

    def _make_change_qrcode_notice_status_request(self, **kwargs) -> requests.Response:
        url = r"http://{host}:{port}/api/change_qrcode_notice_status/{deal_id}".format(
            **kwargs)
        response = requests.get(url=url, headers=self.headers)
        return response

    def _make_get_cities_request(self, **kwargs) -> requests.Response:
        url = r"http://{host}:{port}/api/get_cities".format(**kwargs)
        response = requests.get(url=url, headers=self.headers)
        return response

    def _make_get_questions_request(self, **kwargs) -> requests.Response:
        url = r"http://{host}:{port}/api/get_questions".format(**kwargs)
        response = requests.get(url=url, headers=self.headers)
        return response

    def _make_get_notices_request(self, **kwargs) -> requests.Response:
        url = r"http://{host}:{port}/api/get_notices".format(**kwargs)
        response = requests.get(url=url, headers=self.headers)
        return response

    def _make_get_qrcode_notices_request(self, **kwargs) -> requests.Response:
        url = r"http://{host}:{port}/api/get_qrcode_notices".format(**kwargs)
        response = requests.get(url=url, headers=self.headers)
        return response

    def _make_cancel_deal_request(self, **kwargs) -> requests.Response:
        url = r"http://{host}:{port}/api/cancel_deal/{deal_id}".format(
            **kwargs)
        response = requests.get(url=url, headers=self.headers)
        return response

    def serialize_response_content(self, content) -> dict:
        return json.loads(content)


class WA_API:
    def __init__(self):
        self.email = config.wa_email
        self.password = config.wa_password
        self.wa_token = config.wa_token
        self.license_id = config.wa_license_id
        self.app_id = config.wa_app_id
        self.template_id = config.template_id
        self.headers = {'Content-Type': 'application/json',
                        'Accept': 'application/json'}

    def auth(self):
        url = 'https://api.chatapp.online/v1/tokens'
        payload = {
            "email": self.email,
            "password": self.password,
            "appId": self.app_id
        }

        response = requests.request(
            'POST', url, headers=self.headers, json=payload)
        response = response.json()
        return response

    def send_message(self, phone: str, message_text: str):
        url = F'https://api.chatapp.online/v1/licenses/{self.license_id}/messengers/grWhatsApp/chats/{phone}/messages/text'
        payload = {
            "text": message_text,
        }
        self.headers['Authorization'] = self.wa_token

        response = requests.request(
            'POST', url, headers=self.headers, json=payload)
        response = response.json()

        if not response['success']:
            data = self.auth().get("data")
            if data:
                token = data.get("accessToken")
                config.change_value("WA_TOKEN", token)
                self.wa_token = token
                logger.info("Token regenerated!")
                return self.send_message(phone, message_text)
            error = response['error']
            error_code = error.get("code")
            error_message = error.get("message")
            logger.error(F"{error_code}: {error_message}")
        else:
            return response

    def send_template(self, phone: str, message_text: str):
        url = F'https://api.chatapp.online/v1/licenses/{self.license_id}/messengers/WhatsApp/chats/{phone}/messages/template'
        payload = {
            "template": {
            "id": self.template_id,
            "params": [
                message_text
                ]
            },
            "file": "ipsam",
            "tracking": "vero"
        }

        self.headers['Authorization'] = self.wa_token
        response = requests.request(
            'POST', url, headers=self.headers, json=payload)
        response = response.json()

        if not response['success']:
            data = self.auth().get("data")
            if data:
                token = data.get("accessToken")
                config.change_value("WA_TOKEN", token)
                self.wa_token = token
                logger.info("Token regenerated!")
                return self.send_message(phone, message_text)
            error = response['error']
            error_code = error.get("code")
            error_message = error.get("message")
            logger.error(F"{error_code}: {error_message}")
        else:
            return response
