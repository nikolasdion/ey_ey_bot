""" Classes and methods that handles constructing replies to messages. """

import datetime
from ey_http import Message

# List of strings which triggers an echo response
ECHOED_WORDS = ("ey", "ea", "gelow", "anying")

# Trigger word and reply for when bot is mentioned
CLAPBACK_TRIGGER = "cicing"
CLAPBACK_REPLY = "embung"

# Message broadcasted to chats when bot is back alive
RESSURECTION_MESSAGE = "*BANGKIT DARI KUBUR*"

# The word that's sent at least once a day
EY_OF_THE_DAY_MESSAGE = "ey"


class Replier:
    """ Sends replies to messages """

    _bot_username: str
    _last_ey_day = datetime.datetime.now().day
    _chats_notified = set()

    def __init__(self, bot_username: str):
        self._bot_username = bot_username

    def get_reply(self, message: Message):
        echo = self._get_echo(message.text)
        clapback = self._get_clapback(message.text)
        ey_of_the_day = self._get_ey_of_the_day()
        res_message = self._get_ressurection_message(message.chat_id)

        if res_message is not None:
            return res_message
        elif ey_of_the_day is not None:
            return ey_of_the_day
        elif echo is not None:
            return echo
        elif clapback is not None:
            return clapback
        else:
            return None

    def _get_echo(self, text: str):
        for word in ECHOED_WORDS:
            match = self._get_echo_match(text, word)
            if match is not None:
                print(f"Echo {match}")
                return match
        return None

    @staticmethod
    def _get_echo_match(text: str, word_to_match: str):
        """ Check if the first characters match a given word. """
        truncated_text = text[0 : len(word_to_match)]
        if truncated_text.lower() == word_to_match:
            print(f"Got a match for {word_to_match}")
            return truncated_text
        else:
            return None

    def _get_clapback(self, text: str):
        if self.bot_username in text and CLAPBACK_TRIGGER in text:
            print(f"Reply ${CLAPBACK_REPLY} to ${CLAPBACK_TRIGGER}")
            return CLAPBACK_REPLY
        else:
            return None

    def _get_ey_of_the_day(self):
        # Send an ey if last ey was at least a day ago
        if self._last_ey_day != datetime.datetime.now().day:
            print("Send ey because the last time was at least yesterday")
            self._last_ey_day = datetime.datetime.now().day
            return EY_OF_THE_DAY_MESSAGE
        else:
            return None

    def _get_ressurection_message(self, chat_id: int):
        if not chat_id in self._chats_notified:
            self._chats_notified.add(chat_id)
            print(f"Notify chat {chat_id} that we're back alive!")
            return RESSURECTION_MESSAGE
        else:
            return None
