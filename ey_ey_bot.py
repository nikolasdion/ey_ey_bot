import datetime
import requests
import os
from ey_replies import Replier


class HttpClient:
    """
    Handles all http requests with the Telegram server.
    """

    _last_update = None
    offset = None

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
            print(f"Connected to Telegram server for {bot_display_name} (@{self.bot_username}).")
        else:
            raise ValueError(
                f"Wrong API token. Please check your environment variable."
                f"Response from server: {response}"
            )

    def _get_updates(self):
        params = {
            "timeout": 100,
            "offset": self.offset,
        }
        response = requests.get(self._api_url + "getUpdates", params).json()
        if "result" in response:
            return response["result"]
        else:
            print(f"ERROR: Response doesn't contain result. Full response: {response}")
            return {}

    def get_last_update(self):
        print("Getting latest update...")
        got_last_update = False

        # While we haven't gotten the last update, loop this
        while not got_last_update:
            updates = self._get_updates()
            if len(updates) > 0:
                self._last_update = updates[-1]
                got_last_update = True
            else:
                print("Request timeout or no updates since last time, try sending another request.")

        return self._last_update

    def send_message(self, chat_id, text):
        params = {"chat_id": chat_id, "text": text, "parse_mode": "markdown"}
        response = requests.post(self._api_url + "sendMessage", data=params,)
        print(f"Sent message '{text}', response: {response}")


class Message:
    """
    Represents a message sent in a chat with the bot in it, that this code receives from the
    Telegram server.
    """

    def __init__(self, response_from_server):
        try:
            self.update_id = response_from_server["update_id"]
            self.text = response_from_server["message"]["text"]
            self.chat_id = response_from_server["message"]["chat"]["id"]
            self.sender = response_from_server["message"]["from"]["first_name"]
            self.chat_type = response_from_server["message"]["chat"]["type"]
            # Depending on the chat type, get the title of the chat is either the name of the person
            # or the group name.
            if self.chat_type == "private":
                self.chat_title = self.sender
            else:
                self.chat_title = response_from_server["message"]["chat"]["title"]
        except KeyError:
            print(f"Message from server doesn't have an expected attribute: {response_from_server}")


def main():
    # API token for bot. This is gotten from the environment variable.
    token = os.environ["BOT_TOKEN"]

    http_client = HttpClient(token)
    replier = Replier(http_client)

    while True:
        # Get latest message, this will repeat itself until a non-zero return is gotten.
        message = Message(http_client.get_last_update())

        # TODO: tidy this up!
        # If the "message" object from server is not in the format of a normal chat message (e.g.
        # bot is invited to a new group), the Message object won't have the necessary attributes for
        # the following code to execute. For now, just catch AttributeError.
        try:
            replier.maybe_reply(message)
        except AttributeError as error:
            print(f"Message didn't have the attribute we need. Error was: {error}")

        # Increment offset by 1, for long polling. Catch AttributeError separately so we can still
        # check for the update_id even if the above operation fails. Not updating the offset when
        # we get an update_id means we get the previous message again.
        try:
            http_client.offset = message.update_id + 1
        except:
            print("Failed to update offset, let's hope the bot won't get stuck in a loop...")


if __name__ == "__main__":
    main()
