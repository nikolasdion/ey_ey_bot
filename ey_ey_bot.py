""" Main class, point of entry to run the bot. """

import os
from ey_reply import Replier
from ey_http import HttpClient, Message


def main():
    # API token for bot.
    token = os.environ["BOT_TOKEN"]

    http_client = HttpClient(token)
    replier = Replier(http_client)

    while True:
        # Get latest message, this will repeat itself until a non-zero return is gotten.
        message = http_client.get_last_message()

        replier.maybe_reply(message)


if __name__ == "__main__":
    main()
