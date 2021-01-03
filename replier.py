""" Classes and methods that handles constructing replies to messages. """

from datetime import datetime
from http_client import HttpClient, Message

# List of strings which triggers an echo response
ECHOED_WORDS = ("ey", "ea", "gelow", "anying")

# Trigger word and reply for when bot is mentioned
MENTION_TRIGGER = "cicing"
MENTION_REPLY = "embung"

# Message broadcasted to chats when bot is back alive
RESSURECTION_MESSAGE = "*BANGKIT DARI KUBUR*"

# The word that's sent at least once a day
DAILY_MESSAGE = "ey"


class Replier:
    """ Replies to messages using the supplied HttpClient """

    def __init__(self, http_client: HttpClient):
        self._http_client = http_client
        self._bot_username = http_client.bot_username
        self._last_ey_day = datetime.datetime.now().day
        self._chats_notified = set()

    def reply(self, message: Message):
        reply_text = self._get_reply_text(message)
        if reply_text is not None:
            print(f"Replying {reply_text} to {message.text} in {message.chat_id}")
            self.http_client.send_message(Message(reply_text, message.chat_id))

    def _get_reply_text(self, message: Message):
        return (
            self._get_ressurection_message(message.chat_id)
            or self._get_daily_message(message.chat_id)
            or self._get_mention_reply(message.text)
            or self._get_echo(message.text)
            or None
        )

    def _get_echo(self, text: str):
        for word in ECHOED_WORDS:
            match = self._get_echo_match(text, word)
            if match is not None:
                print(f"Echo {match}")
                return match

    @staticmethod
    def _get_echo_match(text: str, word_to_match: str):
        truncated_text = text[0 : len(word_to_match)]
        if truncated_text.lower() == word_to_match:
            return truncated_text

    def _get_mention_reply(self, text: str):
        if self._bot_username in text and MENTION_TRIGGER in text:
            return MENTION_REPLY

    def _get_daily_message(self):
        if self._last_ey_day != datetime.now().day:
            self._last_ey_day = datetime.now().day
            return DAILY_MESSAGE

    def _get_ressurection_message(self, chat_id: int):
        if not chat_id in self._chats_notified:
            self._chats_notified.add(chat_id)
            return RESSURECTION_MESSAGE
