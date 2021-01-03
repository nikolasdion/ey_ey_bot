""" Classes and methods that handles constructing replies to messages. """

import datetime
from http_client import Message

# List of strings which triggers an echo response
ECHOED_WORDS = ("ey", "ea", "gelow", "anying")

# Trigger word and reply for when bot is mentioned
CLAPBACK_TRIGGER = "cicing"
CLAPBACK_REPLY = "embung"

# Message broadcasted to chats when bot is back alive
RESSURECTION_MESSAGE = "*BANGKIT DARI KUBUR*"

# The word that's sent at least once a day
DAILY_MESSAGE = "ey"


class Replier:
    """ Constructs replies to messages """

    _bot_username: str
    _last_ey_day = datetime.datetime.now().day
    _chats_notified = set()

    def __init__(self, bot_username: str):
        self._bot_username = bot_username

    def get_reply(self, message: Message):
        if self._should_notify_ressurection(message.chat_id):
            return RESSURECTION_MESSAGE

        if self._should_send_daily(message.chat_id):
            return DAILY_MESSAGE

        if self._should_clapback(message.text):
            return CLAPBACK_REPLY

        return self._get_echo(message.text)

    def _get_echo(self, text: str):
        for word in ECHOED_WORDS:
            match = self._get_echo_match(text, word)
            if match is not None:
                print(f"Echo {match}")
                return match
        return None

    @staticmethod
    def _get_echo_match(text: str, word_to_match: str):
        truncated_text = text[0 : len(word_to_match)]
        if truncated_text.lower() == word_to_match:
            return truncated_text
        else:
            return None

    def _should_clapback(self, text: str):
        return self.bot_username in text and CLAPBACK_TRIGGER in text

    def _should_send_daily(self):
        if self._last_ey_day != datetime.datetime.now().day:
            self._last_ey_day = datetime.datetime.now().day
            return True
        else:
            return False

    def _should_notify_ressurection(self, chat_id: int):
        if not chat_id in self._chats_notified:
            self._chats_notified.add(chat_id)
            return True
        else:
            return False
