import time
from typing import Any

from reddit_parser.models import RedditEntity


class MockRedditUser:
    def get_me(self) -> dict[str, Any]:
        return {}


class MockRedditSubreddits:
    def __init__(self, get_top_responses: list, get_new_responses: list[list], get_comments_responses: list[list]) -> None:
        self.get_top_responses = get_top_responses
        self.get_new_responses = get_new_responses
        self.get_comments_responses = get_comments_responses
        self.get_comments_responses_generator = self._get_comments_responses_generator()
        self.get_new_responses_generator = self._get_new_responses_generator()


    def _get_new_responses_generator(self):
        for item in self.get_new_responses:
            yield item

    def _get_comments_responses_generator(self):
        for item in self.get_comments_responses:
            yield item

    def get_top(self, subreddit_name: str, before: str = None) -> list[RedditEntity]:
        result = []
        for x in self.get_top_responses:
            x["created"] = time.time()
            result.append(RedditEntity(**x))
        return result

    def get_new(self, subreddit_name: str, before: str = None, after: str = None) -> list[RedditEntity]:
        result = []
        try:
            for x in next(self.get_new_responses_generator):
                x["created"] = time.time()
                result.append(RedditEntity(**x))
        except StopIteration:
            pass
        return result

    def get_comments(self, subreddit_name: str, article: str) -> list[RedditEntity]:
        result = []
        try:
            for x in next(self.get_comments_responses_generator):
                x["created"] = time.time()
                result.append(RedditEntity(**x))
        except StopIteration:
            pass
        return result


class MockRedditApi:
    def __init__(self, user_mock: MockRedditUser, subreddits_mock: MockRedditSubreddits) -> None:
        self.user = user_mock
        self.subreddits = subreddits_mock
