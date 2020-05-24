import datetime
import requests
import os


# List of strings which triggers an echo response
ECHOED_WORDS = ("ey", "ea", "gelow", "anying")

# Trigger word and reply for when bot is mentioned
CLAPBACK_TRIGGER = "cicing"
CLAPBACK_REPLY = "Embung"

# Message broadcasted to chats when bot is back alive
RESSURECTION_MESSAGE = "*BANGKIT DARI KUBUR*"

# The word that's sent at least once a day
EY_OF_THE_DAY_MESSAGE = "ey"


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


class Echoer:
    """
    Checks messages against a list of words and echoes it back if match is found.
    """

    def maybe_echo(self, message, http_client):
        text = message.text
        echo = self._get_echo(text)
        if echo is not None:
            print(f"Replying '{echo}' for '{text}'")
            http_client.send_message(message.chat_id, echo)

    def _get_echo(self, text):
        for word in ECHOED_WORDS:
            match = self._get_match(text, word)
            if match is not None:
                return match
        return None

    def _get_match(self, text, word_to_match):
        """
        Check if the first characters match a given word.
        """
        truncated_text = text[0 : len(word_to_match)]
        if truncated_text.lower() == word_to_match:
            print(f"Got a match for {word_to_match}")
            return truncated_text
        else:
            return None


class Clapbacker:
    """
    Checks messages against a list of words and echoes it back if match is found.
    """

    def __init__(self, bot_username=""):
        self.bot_username = bot_username

    def maybe_clapback(self, message, http_client):
        text = message.text
        if self._should_clapback(text):
            print(f"Replying '{CLAPBACK_REPLY}' for '{text}'")
            http_client.send_message(message.chat_id, CLAPBACK_REPLY)

    def _should_clapback(self, text):
        return self._is_bot_mentioned(text) and self._contain_trigger_word(text)

    def _contain_trigger_word(self, text):
        return CLAPBACK_TRIGGER in text

    def _is_bot_mentioned(self, text):
        return self.bot_username in text


class EyOfTheDayer:
    """
    Sends out an ey every day.
    """

    _last_ey_day = datetime.datetime.now().day

    def maybe_send(self, message, http_client):
        # Send an ey if last ey was at least a day ago
        if self._last_ey_day != datetime.datetime.now().day:
            print("Sending ey because the last time was at least yesterday")
            http_client.send_message(message.chat_id, EY_OF_THE_DAY_MESSAGE)
            self._last_ey_day = datetime.datetime.now().day


class RessurectionMessenger:
    """
    Notifies every chat that we're alive.
    """

    # Chat IDs
    _chats_notified = set()

    def maybe_send(self, message, http_client):
        chat_id = message.chat_id
        if not chat_id in self._chats_notified:
            http_client.send_message(chat_id, RESSURECTION_MESSAGE)
            self._chats_notified.add(chat_id)
            print(f"Notified chat {message.chat_title} ({chat_id}) that we're back alive!")


def main():
    # API token for bot. This is gotten from the environment variable.
    token = os.environ["BOT_TOKEN"]

    http_client = HttpClient(token)
    echoer = Echoer()
    clapbacker = Clapbacker(http_client.bot_username)
    ey_of_the_dayer = EyOfTheDayer()
    ressurection_messenger = RessurectionMessenger()

    while True:
        # Get latest message, this will repeat itself until a non-zero return is gotten.
        message = Message(http_client.get_last_update())

        # TODO: tidy this up!
        # If the "message" object from server is not in the format of a normal chat message (e.g.
        # bot is invited to a new group), the Message object won't have the necessary attributes for
        # the following code to execute. For now, just catch AttributeError.
        try:
            ressurection_messenger.maybe_send(message, http_client)
            echoer.maybe_echo(message, http_client)
            clapbacker.maybe_clapback(message, http_client)
            ey_of_the_dayer.maybe_send(message, http_client)
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
