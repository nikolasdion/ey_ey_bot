""" Classes and methods that handles HTTP requests to Telegram server. """

import requests
from dataclasses import dataclass


@dataclass
class Message:
    """ Represents a message sent in a chat with the bot in it. """

    text: str
    chat_id: int

    @staticmethod
    def from_server_update(update: dict):
        """
        Create a Message object from a server json response. Returns None if it's not a valid text
        message.
        """
        try:
            text = update["message"]["text"]
            chat_id = update["message"]["chat"]["id"]
            return Message(text, chat_id)
        except KeyError as error:
            print(
                f"Message from server doesn't have an expected attribute, error was: ${error}"
            )
            return None


class HttpClient:
    """ Handles all http requests with the Telegram server. """

    _api_url: str
    _next_request_offset: int
    bot_username: str

    def __init__(self, token: str):
        print("Initialising http client...")
        self._api_url = f"https://api.telegram.org/bot{token}/"
        self._verify_token()
        print("Successfully initialised http client!")

    def _verify_token(self):
        response = requests.get(self._api_url + "getMe").json()
        if response["ok"] and response["result"]["is_bot"]:
            self.bot_username = response["result"]["username"]
            print(f"Token verified for @{self.bot_username}.")
        else:
            raise ValueError(
                f"Invalid API token. Please check your environment variable."
                f"Response from server: {response}"
            )

    def send_message(self, message: Message):
        params = {
            "chat_id": message.chat_id,
            "text": message.text,
            "parse_mode": "markdown",
            "disable_notification": True,
        }
        response = requests.post(
            self._api_url + "sendMessage",
            data=params,
        )
        print(f"Sent message '{text}', response: {response}")

    def get_latest_message(self):
        print("Getting latest update...")

        # Util we get an update, loop this.
        while True:
            updates = self._get_updates()

            if updates == None or len(updates) == 0:
                print(
                    "Request timeout or no updates since last time, try sending another request."
                )
                continue

            update = updates[-1]
            self._next_request_offset = update["update_id"] + 1
            message = Message.from_server_update(update)

            if message is None:
                print("Not a valid text message, wait for another update.")
                continue

            return message

    def _get_updates(self):
        params = {
            "timeout": 100,
            "offset": self._next_request_offset,
        }
        response = requests.get(self._api_url + "getUpdates", params).json()

        if "result" in response:
            return response["result"]
        else:
            print(f"Response doesn't contain result. Full response: {response}")
            return None
