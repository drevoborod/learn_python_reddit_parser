from dataclasses import dataclass
import os


@dataclass
class AuthConfig:
    app_id: str
    secret: str
    username: str
    password: str
    auth_url: str


@dataclass
class Config:
    base_url: str
    auth: AuthConfig


def load_from_env():
    return Config(
        base_url=os.environ["REDDIT_BASE_URL"],
        auth=AuthConfig(
            app_id=os.environ["REDDIT_PARSER_APP_ID"],
            secret=os.environ["REDDIT_PARSER_APP_SECRET"],
            username=os.environ["REDDIT_USER"],
            password=os.environ["REDDIT_PASSWORD"],
            auth_url=os.environ["REDDIT_AUTH_URL"],
        )
    )
