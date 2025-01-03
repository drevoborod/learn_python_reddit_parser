import time
from typing import Any

import httpx
from httpx import Request, Response

from reddit_parser.config import AuthConfig
from reddit_parser.models import RedditEntity, RedditEntityKinds


REQUEST_INTERVAL = 60 / 90


class RedditApiError(Exception): pass
class RedditAuthorizationError(RedditApiError): pass


class Transport(httpx.BaseTransport):
    def __init__(self) -> None:
        self._wrapper = httpx.HTTPTransport()
        self.time_to_wait = 0.0
        self.last_request_timestamp = time.time() - REQUEST_INTERVAL

    def handle_request(self, request: Request) -> Response:
        if self.time_to_wait > 0:
            print(f"Waiting for {self.time_to_wait} seconds for request limits to be restored...")
            time.sleep(self.time_to_wait)
            print("Resuming operations...\n")
        if (allowed_time := (self.last_request_timestamp + REQUEST_INTERVAL)) > (current_time := time.time()):
            time.sleep(allowed_time - current_time)
        response = self._wrapper.handle_request(request)
        self.last_request_timestamp = time.time()
        if (remained_requests := response.headers.get("X-Ratelimit-Remaining")) is not None:
            if float(remained_requests) < 2:
                self.time_to_wait = float(response.headers["X-Ratelimit-Reset"])
        return response


class RedditApi:
    def __init__(self, base_url: str, auth_config: AuthConfig) -> None:
        self.auth_config = auth_config
        headers = {
            "User-Agent": f"linux:{self.auth_config.app_id}:v0.5 (by /u/{self.auth_config.username})",
        }
        self.client = httpx.Client(base_url=base_url, headers=headers, transport=Transport())
        self.user = RedditUser(self.client)
        self.subreddits = RedditSubreddits(self.client)

    def authorize(self) -> None:
        auth = httpx.BasicAuth(self.auth_config.app_id, self.auth_config.secret)
        data = {
            "grant_type": "password",
            "username": self.auth_config.username,
            "password": self.auth_config.password
        }
        response = self.client.post(
            url="https://www.reddit.com/api/v1/access_token", auth=auth, data=data,
        )
        if response.status_code != httpx.codes.OK:
            raise RedditAuthorizationError(f"Authorization failed. Response: {response.json()}")
        self.client.headers["Authorization"] = f"bearer {response.json()['access_token']}"


class RedditUser:
    def __init__(self, client: httpx.Client) -> None:
        self.client = client

    def _get(self, endpoint: str, params: dict = None) -> dict[str, Any] | list[Any]:
        if not params:
            params = {}
        params["raw_json"] = 1
        response = self.client.get(url=endpoint, params=params)
        if response.status_code != httpx.codes.OK:
            raise RedditApiError(f"Response to {endpoint} failed with code {response.status_code}.\n"
                                 f"Body: {response.json()}")
        return response.json()

    def get_me(self) -> dict[str, Any]:
        return self._get(endpoint="/api/v1/me")


class RedditSubreddits:
    def __init__(self, client: httpx.Client) -> None:
        self.client = client

    def _get(self, endpoint: str, params: dict = None) -> dict[str, Any] | list[Any]:
        if not params:
            params = {}
        params["raw_json"] = 1
        response = self.client.get(url=endpoint, params=params)
        if response.status_code != httpx.codes.OK:
            raise RedditApiError(f"Response to {endpoint} failed with code {response.status_code}.\n"
                                 f"Body: {response.json()}")
        return response.json()

    def get_top(self, subreddit_name: str, before: str = None) -> list[RedditEntity]:
        params = {
            "t": "all",
            "limit": 100,
        }
        if before:
            params["before"] = before

        result = self._get(
            endpoint=f"/r/{subreddit_name}/top",
            params=params,
        )
        return _convert_reddit_response_to_models(result["data"]["children"])

    def get_new(self, subreddit_name: str, before: str = None, after: str = None) -> list[RedditEntity]:
        params = {
            "limit": 100,
        }
        if before:
            params["before"] = before
        if after:
            params["after"] = after

        result = self._get(
            endpoint=f"/r/{subreddit_name}/new",
            params=params,
        )
        return _convert_reddit_response_to_models(result["data"]["children"])

    def get_comments(self, subreddit_name: str, article: str) -> list[RedditEntity]:
        params = {"sort": "new", "depth": 100}
        result = self._get(
            endpoint=f"/r/{subreddit_name}/comments/{article}",
            params=params,
        )
        return _convert_reddit_response_to_models(result[1]["data"]["children"])


def _convert_reddit_response_to_models(data: list[dict[str, Any]]) -> list[RedditEntity]:
    return [
        RedditEntity(
            id=item["data"]["id"],
            author=item["data"]["author"],
            created=item["data"]["created"],
            name=item["data"]["name"],
            kind=item["kind"],
            score=item["data"]["score"]
        ) for item in data if item["kind"] in RedditEntityKinds
    ]
