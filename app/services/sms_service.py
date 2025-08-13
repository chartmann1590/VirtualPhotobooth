import requests
from typing import List


class SMSGateClient:
    def __init__(self, api_base: str, username: str, password: str) -> None:
        self.api_base = api_base.rstrip('/')
        self.username = username
        self.password = password

    def send_sms(self, message: str, phone_numbers: List[str]) -> requests.Response:
        url = f"{self.api_base}/3rdparty/v1/message"
        response = requests.post(
            url,
            auth=(self.username, self.password),
            json={
                "message": message,
                "phoneNumbers": phone_numbers,
            },
            timeout=20,
        )
        response.raise_for_status()
        return response
