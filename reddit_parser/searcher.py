from abc import ABC
from datetime import datetime, timedelta
from typing import Any

from reddit_parser.api import RedditApi
from reddit_parser.models import RedditEntity

type Json = dict[str, Any] | list[dict[str, Any]]


class Searcher(ABC):
    def __init__(self, api: RedditApi) -> None:
        self.api = api

    def get(self, subreddit_name: str, days: int = 3) -> list[Any] | dict[str, Any]:
        """Returns list of filtered subreddit's 'links' or another info in a JSON-ready structure."""


class TopLinksSearcher(Searcher):
    def get(self, subreddit_name: str, days: int = 3) -> list[dict[str, Any]]:
        threshold = datetime.now() - timedelta(days=days)
        links = self.get_links_from_api(subreddit_name)
        if not links:
            return []

        while True:
            oldest_timestamp = datetime.fromtimestamp(links[-1].created)
            if oldest_timestamp > threshold:
                links.extend(self.get_links_from_api(subreddit_name, before=links[-1].name))
            else:
                index = locate_closest_link_index(links, threshold)
                ordered = self._sort_links_by_score(links[:index])
                return [x.model_dump() for x in ordered]

    def get_links_from_api(self, subreddit_name: str, before: str = None) -> list[RedditEntity]:
        res = self.api.subreddits.get_top(subreddit_name, before=before)
        return sorted(res, key=lambda x: x.created, reverse=True)

    def _sort_links_by_score(self, links: list[RedditEntity]):
        return sorted(links, key=lambda x: x.score, reverse=True)


class TopUsersSearcher(Searcher):
    def get(self, subreddit_name: str, days: int = 3) -> dict[str, list[str]]:
        threshold = datetime.now() - timedelta(days=days)
        links = self.get_links_from_api(subreddit_name)
        result = {
                    "top_users_by_posts": [],
                    "top_users_by_comments": [],
                }
        if not links:
            return result

        while True:
            oldest_timestamp = datetime.fromtimestamp(links[-1].created)
            if oldest_timestamp > threshold:
                new_links = self.get_links_from_api(subreddit_name, before=links[-1].name)
                if new_links:
                    links.extend(new_links)
                else:
                    break
        index = locate_closest_link_index(links, threshold)
        result["top_users_by_posts"] = self._top_users_by_posts(links[:index])
        result["top_users_by_comments"] = self._top_users_by_comments(subreddit_name,  links[:index])
        return result

    def get_links_from_api(self, subreddit_name: str, before: str = None, after: str = None) -> list[RedditEntity]:
        res = self.api.subreddits.get_new(subreddit_name, before=before, after=after)
        return sorted(res, key=lambda x: x.created, reverse=True)

    def _top_users_by_comments(self, subreddit_name: str, links: list[RedditEntity]) -> list[str]:
        link_comments_dict = {link.id: self.api.subreddits.get_comments(subreddit_name, link.id) for link in links}
        authors = {}
        for comment_list in link_comments_dict.values():
            for comment in comment_list:
                authors[comment.author] = authors.get(comment.author, 0) + 1
        # return sorted(authors, key=lambda x: authors[x], reverse=True)
        return [f"{author}: {authors[author]}" for author in sorted(authors, key=lambda x: authors[x], reverse=True)]

    def _top_users_by_posts(self, links: list[RedditEntity]) -> list[str]:
        users_posts = {}
        for link in links:
            users_posts[link.author] = users_posts.get(link.author, 0) + 1
        return [f"{author}: {users_posts[author]}" for author in sorted(users_posts, key=lambda x: users_posts[x], reverse=True)]


def locate_closest_link_index(links: list[RedditEntity], timestamp: datetime) -> int:
    for index, value in enumerate(links):
        if datetime.fromtimestamp(value.created) < timestamp:
            return index
    return len(links)
