import json
import logging
from http import HTTPStatus

import requests


class StackOverflowAPI:
    API_URL = "https://api.stackexchange.com"
    logger = logging.getLogger("StackOverflowAPI")

    @staticmethod
    def _api_call(url, params):
        response = requests.get(StackOverflowAPI.API_URL + url, params=params)

        if response.status_code != HTTPStatus.OK:
            StackOverflowAPI.logger.error("Failed to make API call: status_code = {}".format(response.status_code))
            return

        return response

    @staticmethod
    def posts(ids, sort="votes"):
        """Get posts by ids"""

        url = "/2.2/posts/{ids}".format(ids=";".join(map(lambda it: str(it), ids)))

        params = {
            "order": "desc",
            "sort": sort,
            "site": "stackoverflow",
            "filter": "withbody"
        }

        response = StackOverflowAPI._api_call(url, params)
        if response is not None:
            return json.loads(response.text).get("items")

        return []

    @staticmethod
    def search(question, sort="relevance"):
        """Get questions by question text"""

        url = "/2.2/search/advanced"

        params = {
            "order": "desc",
            "sort": sort,
            "site": "stackoverflow",
            "q": question
        }

        response = StackOverflowAPI._api_call(url, params)
        if response is not None:
            return json.loads(response.text).get("items")

        return []

    @staticmethod
    def answers(ids, sort="votes"):
        """Get answers by questions' ids"""

        url = "/2.2/questions/{ids}/answers".format(ids=";".join(map(lambda it: str(it), ids)))

        params = {
            "order": "desc",
            "sort": sort,
            "site": "stackoverflow",
            "filter": "withbody"
        }

        response = StackOverflowAPI._api_call(url, params)
        if response is not None:
            return json.loads(response.text).get("items")

        return []
