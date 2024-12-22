import time
from dataclasses import dataclass
from http import HTTPStatus
from os import environ
from typing import Literal

import requests
from requests.auth import HTTPBasicAuth


REQUEST_INTERVAL = 60 / 90


class RedditApiError(Exception): pass


@dataclass
class AuthParams:
    app_id: str = environ.get("REDDIT_PARSER_APP_ID")
    secret: str = environ.get("REDDIT_PARSER_APP_SECRET")
    username: str = environ.get("REDDIT_USER")
    password: str = environ.get("REDDIT_PASSWORD")

    def __post_init__(self):
        for key, value in self.__dict__.items():
            if value is None:
                raise RedditApiError(f"Environment variable containing {key} was not found")


class RedditApiBase:
    def __init__(self):
        self.auth_url = "https://www.reddit.com/api/v1/access_token"
        self.base_url = "https://oauth.reddit.com"
        self.auth_params = AuthParams()
        self.token: str = ""
        self.last_request_timestamp: float = time.time() - REQUEST_INTERVAL
        self.default_headers = {"User-Agent": f"linux:{self.auth_params.app_id}:v0.5 (by /u/{self.auth_params.username})"}

    def authorize(self):
        auth = HTTPBasicAuth(self.auth_params.app_id, self.auth_params.secret)
        data = {
            "grant_type": "password",
            "username": self.auth_params.username,
            "password": self.auth_params.password
        }
        response = requests.post(url="https://www.reddit.com/api/v1/access_token", auth=auth, data=data,
                                 headers=self.default_headers)
        if response.status_code != HTTPStatus.OK:
            raise RedditApiError(f"Authorization failed. Response: {response.json()}")
        self.token = response.json()["access_token"]

    def send(
        self,
        method: Literal["GET", "get", "POST", "post"],
        endpoint: str,
        additional_headers: dict = None,
        body: dict = None,
    ) -> dict:
        if not self.token:
            self.authorize()
        if not additional_headers:
            additional_headers = {}
        additional_headers["Authorization"] = f"bearer {self.token}"
        additional_headers.update(self.default_headers)
        if need_to_wait := (self.last_request_timestamp + REQUEST_INTERVAL) > time.time():
            time.sleep(need_to_wait - time.time())
        response = requests.request(
            method, url=self.base_url + endpoint, headers=additional_headers, json=body, params={"raw_json": 1})
        if response.status_code != HTTPStatus.OK:
            raise RedditApiError(f"Response to {endpoint} failed with code {response.status_code}.\n"
                                 f"Body: {response.json()}")
        return response.json()


class RedditUserInfo(RedditApiBase):
    def me(self):
        return self.send("get", endpoint="/api/v1/me")


