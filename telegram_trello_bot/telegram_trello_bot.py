"""
This is a main source file for telegram_trello_bot.
"""
import asyncio
import io
import logging
import os
import sys
import tempfile
import time
from typing import Optional

import argparse
import arrow
import telegram
import toml

from trello_wrapper import Trello

CONFIG_FILE="config.toml"

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# For debugging
#log.setLevel(logging.DEBUG)


def parse_arguments(args: list) -> argparse.Namespace:
    """
    Parse arguments for the script.

    Params:
      args:Application arguments to parse.

    Returns:
      Parsed arguments as argparse.Namespace.
    """
    parser = argparse.ArgumentParser(
        description="Simple telegram bot for trello notifications."
    )

    parser.add_argument(
        "--config",
        help="Configuration file"
    )

    return parser.parse_args()


def read_config(config: str) -> dict:
    """
    Read config file. If none is provided it will try DEFAULT_CONFIG_FILE.

    Params:
      Path to config file.

    Returns:
      Parsed configuration as dict.

    Raises:
      RuntimeError: When no configuration file could be found.
    """
    if config:
        log.debug("Reading config '{}'".format(config))
        if os.path.isfile(config):
            return toml.load(config)

    else:
        log.debug("Reading config '{}'".format(CONFIG_FILE))
        if os.path.isfile(CONFIG_FILE):
            return toml.load(CONFIG_FILE)

    raise RuntimeError("No configuration file found.")


# In newer versions of python-telegram-bot library
# we need to have async function to send messages
async def send_message(bot: telegram.Bot, chat_id: int, message: str) -> None:
    """
    Sends messages to telegram.

    Params:
      bot: Instance of the bot to use to send message
      chat_id: ID of the chat to send message to
      message: Message to send
    """
    log.debug("Sending message to telegram: %s", message)
    await bot.send_message(
        chat_id,
        message,
        parse_mode=telegram.constants.ParseMode.MARKDOWN_V2,
    )


if __name__ == "__main__":
    log.debug("Parsing arguments '{}'".format(sys.argv[1:]))
    args = parse_arguments(sys.argv[1:])
    config = read_config(args.config)

    log.debug("Initializing trello object")
    trello = Trello(
        config.get("trello_api_key"),
        config.get("trello_api_secret"),
        config.get("trello_token"),
    )
    log.debug("Initializing telegram bot")
    bot = telegram.Bot(token=config.get("bot_api_token"))

    # Is first day of the month?
    now = arrow.utcnow()
    if now.date().day == 1:
        # Shift the date to end of month
        till = now.ceil('month')
    else:
        # If not start of the month just retrieve cards
        # for upcoming week
        till = now.shift(days=+7)

    # Get the cards for the range
    cards = sorted(trello.get_upcoming_cards(till), key=lambda x:x[1])
    log.debug(cards)

    # If nothing was retrieved, no need to send anything
    log.info("Retrieved %d cards from trello", len(cards))
    if cards:

        upcoming_week = []
        upcoming_month = []

        for name, due_date, url in cards:
            text = "[{}]({}) \\- {}".format(
                telegram.helpers.escape_markdown(name, version=2),
                telegram.helpers.escape_markdown(url, version=2),
                telegram.helpers.escape_markdown(due_date.to('local').format("DD-MM-YYYY HH:mm"), version=2)
            )
            # Only fill upcoming Month if it's first day of month
            if now.date().day == 1:
                upcoming_month.append(text)
            # Don't add any cards with due_date greater than till to
            # weekly upcoming cards
            if due_date <= till:
                upcoming_week.append(text)

        # Prepare messages to sent to telegram
        monthly_message = ""
        if len(upcoming_month) > 0:
            monthly_message = "In *{}* :\n".format(now.format("MMM"))
            for entry in upcoming_month:
                monthly_message = monthly_message + "\\- {}\n".format(entry)

        weekly_message = "In *next 7 days* :\n"
        for entry in upcoming_week:
            weekly_message = weekly_message + "\\- {}\n".format(entry)

        if monthly_message:
            log.debug("Monthly message to send: %s", monthly_message)
            asyncio.run(send_message(bot, config.get("telegram_chat_id"), monthly_message))

        log.debug("Weekly message to send: %s", weekly_message)
        asyncio.run(send_message(bot, config.get("telegram_chat_id"), weekly_message))
