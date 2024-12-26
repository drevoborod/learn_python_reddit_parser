import argparse
import string
import json

from reddit_parser.searcher import TopSearcher


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

def save(name: str, data: dict | list):
    with open(name, "w") as file:
        file.write(json.dumps(data, indent=4))


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("subreddit", help="Subreddit name to search links in.")
    parser.add_argument("-d", "--days", help="Count of days.", required=False, type=int)
    return parser.parse_args()


def main(report_filename: str = "top_links.json"):
    params = get_args()
    if not params.days:
        params.days = 3
    searcher = TopSearcher()
    save(report_filename, searcher.get(params.subreddit, params.days))


if __name__ == "__main__":
    main()
