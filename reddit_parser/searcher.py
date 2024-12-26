import json
import string
from copy import deepcopy
from datetime import datetime, timedelta
from typing import Protocol

from reddit_parser.api import RedditSubreddits


class Searcher(Protocol):
    def get(self, subreddit_name: str, days: int = 3) -> list:
        """Returns list of filtered subreddit's 'links' or another info in a JSON-ready structure."""


class TopLinksSearcher(Searcher):
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
        return sorted(links, key=lambda x: x["data"]["created"], reverse=True)

    def _sort_links_by_score(self, links):
        return sorted(links, key=lambda x: x["data"]["score"])


class TopUsersSearcher(Searcher):
    def __init__(self):
        self.api = RedditSubreddits()

    def get(self, subreddit_name: str, days: int = 3) -> list[str]:
        threshold = datetime.now() - timedelta(days=days)
        links = self.get_links_from_api(subreddit_name)

        while True:
            oldest_timestamp = datetime.fromtimestamp(links[-1]["data"]["created"])
            if oldest_timestamp > threshold:
                links.extend(self.get_links_from_api(subreddit_name, before=links[-1]["data"]["name"]))
            else:
                index = locate_closest_link(links, threshold)
                return self._top_users_by_posts(links[:index])

    def get_links_from_api(self, subreddit_name: str, before: str = None, after: str = None) -> list:
        res = self.api.new(subreddit_name, before=before, after=after)
        links = deepcopy(res["data"]["children"])
        return sorted(links, key=lambda x: x["data"]["created"], reverse=True)

    def _top_users_by_comments(self, links: list[dict]):
        pass

    def _top_users_by_posts(self, links: list[dict]) -> list[str]:
        users_posts = {}
        for link in links:
            users_posts[link["data"]["author_fullname"]] = users_posts.get(link["data"]["author_fullname"], 0) + 1
        return sorted(users_posts, key=lambda x: users_posts[x], reverse=True)


def locate_closest_link(arr: list, timestamp: datetime) -> int:
    for index, value in enumerate(arr):
        if datetime.fromtimestamp(value["data"]["created"]) < timestamp:
            return index
    return 0


def to_base(number: int, base: int=36) -> str:
    """Converts a non-negative number to a list of digits in the given base.

    """
    symbols = string.digits + string.ascii_lowercase
    if not number:
        return "0"

    digits = []
    while number:
        digits.append(symbols[number % base])
        number //= base
    return "".join(list(reversed(digits)))
