from copy import deepcopy
from datetime import datetime, timedelta
from typing import Protocol

from reddit_parser.api import RedditSubreddits


class Searcher(Protocol):
    def get(self, subreddit_name: str) -> list[dict]:
        """Returns list of filtered subreddit's 'links'"""


class TopSearcher(Searcher):
    def __init__(self):
        self.api = RedditSubreddits()

    def get(self, subreddit_name: str, days: int = 3) -> list[dict]:
        threshold = datetime.now() - timedelta(days=days)
        links = self.get_links_from_api(subreddit_name)

        while True:
            oldest_timestamp = datetime.fromtimestamp(links[-1]["data"]["created"])
            if oldest_timestamp > threshold:
                links.extend(self.get_links_from_api(subreddit_name, before=links[-1]["data"]["name"]))
            else:
                index = locate_closest_link(links, threshold)
                return self._sort_links_by_score(links[:index])

    def get_links_from_api(self, subreddit_name: str, before: str = None) -> list:
        res =self.api.top(subreddit_name, before=before)
        links = deepcopy(res["data"]["children"])
        return list(reversed(sorted(links, key=lambda x: x["data"]["created"])))

    def _sort_links_by_score(self, links):
        return sorted(links, key=lambda x: x["data"]["score"])


class LinksSearcher(Searcher):
    def get(self, subreddit_name: str) -> list[dict]:
        pass



def locate_closest_link(arr: list, timestamp: datetime) -> int:
    for index, value in enumerate(arr):
        if datetime.fromtimestamp(value["data"]["created"]) < timestamp:
            return index
    return 0