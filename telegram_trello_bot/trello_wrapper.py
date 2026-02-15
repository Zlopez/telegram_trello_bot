"""
Trello wrapper using py-trello library.
"""
import logging
from typing import Tuple, List

import arrow
from trello import TrelloClient

log = logging.getLogger(__name__)

# For debugging
#log.setLevel(logging.DEBUG)

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
    ) -> List[Tuple[str, arrow.Arrow, str]]:
        """
        Collect all cards from Trello that have due date since now till `till`.

        Params:
          till: Due date for retrived cards

        Returns:
          List of tuples containing Due Date, Name and link to card
        """
        now = arrow.utcnow()
        result = []
        for board in self._trello.list_boards():
            log.info("Processing board %s ...", board.name)
            for trello_list in board.list_lists():
                log.info("Processing list %s ...", trello_list.name)
                for card in trello_list.list_cards():
                    # Skip cards without due dates
                    if not card.due_date:
                        log.debug("%s doesn't have due date set. Skipping.", card.name)
                        continue
                    due_date = arrow.get(card.due_date)
                    log.debug("%s has date %s", card.name, due_date)
                    log.debug("%s < %s < %s", now, due_date, till)
                    if due_date < till and due_date > now:
                        # This is the card we want to be notified about
                        result.append((card.name, due_date, card.url))

        return result
