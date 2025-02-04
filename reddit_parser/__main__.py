import argparse
import json
import os
from enum import StrEnum
from typing import Any, Callable
from collections.abc import Hashable

from reddit_parser.searcher import TopLinksSearcher, TopUsersSearcher
from reddit_parser.api import RedditApi
from reddit_parser.config import load_from_env, Config


class TopMode(StrEnum):
    TOP_LINKS = "top_links"
    TOP_USERS = "top_users"


def save(name: str, data: dict[Hashable, Any] | list[Any]) -> None:
    with open(name, "w") as file:
        file.write(json.dumps(data, indent=4))


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("subreddit", help="Subreddit name to search links in.")
    parser.add_argument("-d", "--days", help="Count of days.", required=False, type=int, default=3)
    parser.add_argument(
        "-m", "--mode", help="Rating mode. One of: top_links, top_users.",
        required=False, type=TopMode, default=TopMode.TOP_USERS,
    )
    parser.add_argument(
        "-f", "--file", help="File name to save results into.",
        required=False, type=str, default="result.json"
    )
    parser.add_argument("--log", help="Enable saving responses to a log file", action="store_true")
    return parser.parse_args()


def create_searcher(params: argparse.Namespace, config: Config) -> Callable[[str, int], ...]:
    api = RedditApi(base_url=config.base_url, auth_config=config.auth)
    match params.mode:
        case TopMode.TOP_LINKS:
            searcher = TopLinksSearcher(api)
        case TopMode.TOP_USERS:
            searcher = TopUsersSearcher(api)
        case _:
            raise ValueError(f"Unknown mode: {params.mode}")
    searcher.api.authorize()
    return searcher.process


def main() -> str:
    params = get_args()
    os.environ["ENABLE_REDDIT_PARSER_LOGGING"] = str(params.log)
    config = load_from_env()
    searcher = create_searcher(params, config)
    report_filename = params.file
    result = searcher(params.subreddit, params.days)
    save(report_filename, result)
    return f"Results saved to {report_filename}."


if __name__ == "__main__":
    print(main())
