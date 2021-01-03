""" Main class, point of entry to run the bot. """

import os
from replier import Replier
from http_client import HttpClient


def main():
    # API token for bot.
    token = os.environ["BOT_TOKEN"]

    http_client = HttpClient(token)
    replier = Replier(http_client.bot_username)

    while True:
        # Get latest message, this will repeat itself until a non-None return is gotten.
        message = http_client.get_latest_message()

        reply = replier.get_reply(message)
        if reply is not None:
            print(f"Replying {reply} to {message.text} in {message.chat_id}")
            http_client.send_message(message.chat_id, reply)


if __name__ == "__main__":
    main()
