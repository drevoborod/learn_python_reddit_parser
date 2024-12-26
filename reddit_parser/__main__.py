import argparse
import json
from enum import StrEnum

from reddit_parser.searcher import TopLinksSearcher, Searcher, TopUsersSearcher


class TopMode(StrEnum):
    TOP_LINKS = "top_links"
    TOP_USERS = "top_users"


def save(name: str, data: dict | list):
    with open(name, "w") as file:
        file.write(json.dumps(data, indent=4))


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("subreddit", help="Subreddit name to search links in.")
    parser.add_argument("-d", "--days", help="Count of days.", required=False, type=int, default=3)
    parser.add_argument(
        "-m", "--mode", help="Count of days.",
        required=False, type=TopMode, default=TopMode.TOP_USERS
    )
    return parser.parse_args()


def main(report_filename: str = "result.json") -> str:
    params = get_args()
    match params.mode:
        case TopMode.TOP_LINKS:
            searcher: Searcher = TopLinksSearcher()
        case TopMode.TOP_USERS:
            searcher: Searcher = TopUsersSearcher()
        case _:
            return f"Unknown mode: {params.mode}"
    save(report_filename, searcher.get(params.subreddit, params.days))
    return f"Results saved to {report_filename}."


if __name__ == "__main__":
    print(main())
