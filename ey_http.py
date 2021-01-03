""" Classes and methods that handles HTTP requests to Telegram server. """

import requests
from dataclasses import dataclass


@dataclass
class Message:
    """ Represents a message sent in a chat with the bot in it. """

    text: str
    chat_id: int
    sender: str
    chat_type: str
    chat_title: str


class HttpClient:
    """ Handles all http requests with the Telegram server. """

    _next_request_offset = None

    def __init__(self, token):
        print("Initialising http client...")
        self._token = token
        self._api_url = f"https://api.telegram.org/bot{token}/"
        self._verify_token()
        print("Successfully initialised http client!")

    def _verify_token(self):
        response = requests.get(self._api_url + "getMe").json()
        if response["ok"] == True and response["result"]["is_bot"] == True:
            bot_display_name = response["result"]["first_name"]
            self.bot_username = response["result"]["username"]
            print(
                f"Connected to Telegram server for {bot_display_name} (@{self.bot_username})."
            )
        else:
            raise ValueError(
                f"Wrong API token. Please check your environment variable."
                f"Response from server: {response}"
            )

    def send_message(self, chat_id, text):
        params = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "markdown",
            "disable_notification": True,
        }
        response = requests.post(
            self._api_url + "sendMessage",
            data=params,
        )
        print(f"Sent message '{text}', response: {response}")

    def get_last_message(self):
        last_update = self._get_last_update()
        return self._message_from_update(last_update)

    def _get_updates(self):
        params = {
            "timeout": 100,
            "offset": self._next_request_offset,
        }
        response = requests.get(self._api_url + "getUpdates", params).json()
        if "result" in response:
            return response["result"]
        else:
            print(f"ERROR: Response doesn't contain result. Full response: {response}")
            return {}

    def _get_last_update(self):
        print("Getting latest update...")

        # Util we get an update, loop this.
        while True:
            updates = self._get_updates()
            if len(updates) > 0:
                update = updates[-1]
                self._next_request_offset = update["update_id"] + 1
                return update
            else:
                print(
                    "Request timeout or no updates since last time, try sending another request."
                )

    def _message_from_update(self, update):
        try:
            text = update["message"]["text"]
            chat_id = update["message"]["chat"]["id"]
            sender = update["message"]["from"]["first_name"]
            chat_type = update["message"]["chat"]["type"]
            # Depending on the chat type, get the title is either the name of the person or the
            # group name.
            if chat_type == "private":
                chat_title = sender
            else:
                chat_title = update["message"]["chat"]["title"]

            return Message(text, chat_id, sender, chat_type, chat_title)
        except KeyError:
            print(f"Message from server doesn't have an expected attribute")
            return None
