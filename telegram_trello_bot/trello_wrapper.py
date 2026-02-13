"""
Trello wrapper using py-trello library.
"""
import logging
from typing import Dict, Tuple

import arrow
from trello import TrelloClient

log = logging.getLogger(__name__)


class Trello:
    """
    Trello class for communicating with trello server.
    """
    # private TrelloClient object
    _trello: TrelloClient = None

    def __init__(
            self,
            api_key: str,
            api_secret: str,
            token: str
    ) -> None:
        """
        Initializes the Nextcloud instance.

        Params:
          api_key: Trello API key
          api_secret: Trello API secret
          token: Trello API token
        """
        log.debug(
            "Creating the trello object with api_key: %s, api_secret: %s, token: %s",
            api_key, api_secret, token
        )
        self._trello = TrelloClient(
            api_key=api_key,
            api_secret=api_secret,
            token=token
        )

    def get_upcoming_cards(
            self,
            till: arrow.Arrow
    ) -> Dict[arrow.Arrow, Tuple[str, str]]:
        """
        Collect all cards from Trello that have due date since now till `till`.

        Params:
          till: Due date for retrived cards

        Returns:
          Dictionary containing Due Date, Name and link to card
        """
        now = arrow.utcnow()
        result = {}
        for board in self._trello.list_boards():
            for trello_list in board.list_lists():
                for card in trello_list.list_cards():
                    # Skip cards without due dates
                    if not card.due_date:
                        continue
                    due_date = arrow.get(card.due_date)
                    log.debug("%s has date %s", card.name, due_date)
                    if due_date < till and due_date > now:
                        # This is the card we want to be notified about
                        result[due_date] = (card.name, card.url)

        return result
