# telegram_upload_bot
Simple telegram bot to notify about upcoming trello events

This bot is looking at cards on Trello server and sends notification
to specified room for upcoming events in upcoming month (on first day of
the month) and in next 7 days.

## Quick start
1. Clone the repository
  `git clone https://github.com/Zlopez/telegram_trello_bot.git`

2. Create a python virtualenv
  `python -m venv .venv`

3. Create config file
  `cp config.toml.example config.toml`

4. Update the config file. See comments for more info.

5. Run the bot
  `python telegram_trello_bot/telegram_trello_bot.py`

---

## Configuration

The configuration is using [toml](https://en.wikipedia.org/wiki/TOML) format
and there is example in this repository.

The bot supports multiple configurations. You just need to start it with `--config`
parameter:

`python telegram_trello_bot/telegram_trello_bot.py --config <path_to_config>`
