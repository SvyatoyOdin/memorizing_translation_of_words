import requests
import time


class Bot:
    """this class working with telegram API """
    def __init__(self, url: str, user_id: int) -> None:
        self.url = url
        self.user_id = user_id

    def get_updates(self) -> dict:
        response = requests.get(f"{self.url}/getUpdates")
        if response.status_code != 200:
            raise Exception(f"status code - {response.status_code}")
        time.sleep(1.5)
        return response.json()

    def send_message(self, text: str, parse_mode: str = None) -> None:
        """send message to user"""
        data = {"chat_id": self.user_id, "text": text, "parse_mode": parse_mode}
        requests.post(f"{self.url}/sendMessage", data=data)

    def delete_message(self, chat_id: int, message_id: int) -> None:
        """"delete message user"""
        data = {"chat_id": chat_id, "message_id": message_id}
        requests.post(f"{self.url}/deleteMessage", data=data)
