""" Classes and methods that handles constructing replies to messages. """

import datetime

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

    def __init__(self, http_client):
        self._http_client = http_client
        self._echoer = Echoer()
        self._clapbacker = Clapbacker(http_client.bot_username)
        self._ey_of_the_dayer = EyOfTheDayer()
        self._ressurection_messenger = RessurectionMessenger()

    def maybe_reply(self, message):
        # TODO: tidy this up!
        # If the "message" object from server is not in the format of a normal chat message (e.g.
        # bot is invited to a new group), the Message object won't have the necessary attributes for
        # the following code to execute. For now, just catch AttributeError.
        try:
            # Disabled for now because it's getting annoying
            # TODO: re-enable once no longer crashing when receiving images
            # self._ressurection_messenger.maybe_send(message, self._http_client) 
            self._echoer.maybe_echo(message, self._http_client)
            self._clapbacker.maybe_clapback(message, self._http_client)
            self._ey_of_the_dayer.maybe_send(message, self._http_client)
        except AttributeError as error:
            print(f"Message didn't have the attribute we need. Error was: {error}")


class Echoer:
    """ Checks messages against a list of words and echoes it back if match is found. """

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
        """ Check if the first characters match a given word. """
        truncated_text = text[0 : len(word_to_match)]
        if truncated_text.lower() == word_to_match:
            print(f"Got a match for {word_to_match}")
            return truncated_text
        else:
            return None


class Clapbacker:
    """ Checks messages against a list of words and echoes it back if match is found. """

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
    """ Sends out an ey every day. """

    _last_ey_day = datetime.datetime.now().day

    def maybe_send(self, message, http_client):
        # Send an ey if last ey was at least a day ago
        if self._last_ey_day != datetime.datetime.now().day:
            print("Sending ey because the last time was at least yesterday")
            http_client.send_message(message.chat_id, EY_OF_THE_DAY_MESSAGE)
            self._last_ey_day = datetime.datetime.now().day


class RessurectionMessenger:
    """ Notifies every chat that we're alive. """

    _chats_notified = set()

    def maybe_send(self, message, http_client):
        chat_id = message.chat_id
        if not chat_id in self._chats_notified:
            http_client.send_message(chat_id, RESSURECTION_MESSAGE)
            self._chats_notified.add(chat_id)
            print(f"Notified chat {message.chat_title} ({chat_id}) that we're back alive!")
