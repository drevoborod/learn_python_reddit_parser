import string
from abc import ABC
from copy import deepcopy
from datetime import datetime, timedelta
from typing import Any

from reddit_parser.api import RedditApi


type Json = dict[str, Any] | list[dict[str, Any]]


class Searcher(ABC):
    def __init__(self, api: RedditApi):
        self.api = api

    def get(self, subreddit_name: str, days: int = 3) -> list | dict:
        """Returns list of filtered subreddit's 'links' or another info in a JSON-ready structure."""


class TopLinksSearcher(Searcher):
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
        res = self.api.subreddits.get_top(subreddit_name, before=before)
        links = deepcopy(res["data"]["children"])
        return sorted(links, key=lambda x: x["data"]["created"], reverse=True)

    def _sort_links_by_score(self, links):
        return sorted(links, key=lambda x: x["data"]["score"])


class TopUsersSearcher(Searcher):
    def get(self, subreddit_name: str, days: int = 3) -> dict[str, list[str]]:
        threshold = datetime.now() - timedelta(days=days)
        links = self.get_links_from_api(subreddit_name)

        while True:
            oldest_timestamp = datetime.fromtimestamp(links[-1]["data"]["created"])
            if oldest_timestamp > threshold:
                links.extend(self.get_links_from_api(subreddit_name, before=links[-1]["data"]["name"]))
            else:
                index = locate_closest_link(links, threshold)
                return {
                    "top_users_by_posts": self._top_users_by_posts(links[:index]),
                    "top_users_by_comments": self._top_users_by_comments(subreddit_name,  links[:index]),
                }

    def get_links_from_api(self, subreddit_name: str, before: str = None, after: str = None) -> list:
        res = self.api.subreddits.get_new(subreddit_name, before=before, after=after)
        links = deepcopy(res["data"]["children"])
        return sorted(links, key=lambda x: x["data"]["created"], reverse=True)

    def _top_users_by_comments(self, subreddit_name: str, links: list[dict]) -> list[str]:
        comments_dict = {link["data"]["id"]: self.api.subreddits.get_comments(subreddit_name, link["data"]["id"]) for link in links}
        authors = {}
        for comment_data in comments_dict.values():
            for comment_branch in comment_data:
                for comment in comment_branch["data"]["children"]:
                    authors[comment["data"]["author"]] = authors.get(comment["data"]["author"], 0) + 1
        # return sorted(authors, key=lambda x: authors[x], reverse=True)
        return [f"{author}: {authors[author]}" for author in sorted(authors, key=lambda x: authors[x], reverse=True)]

    def _top_users_by_posts(self, links: list[dict]) -> list[str]:
        users_posts = {}
        for link in links:
            users_posts[link["data"]["author"]] = users_posts.get(link["data"]["author"], 0) + 1
        return [f"{author}: {users_posts[author]}" for author in sorted(users_posts, key=lambda x: users_posts[x], reverse=True)]


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
