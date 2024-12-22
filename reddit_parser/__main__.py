import string
import json

from reddit_parser.api import RedditUserInfo


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


def main():
    api = RedditUserInfo()
    res = api.me()
    print(json.dumps(res, indent=4))


if __name__ == "__main__":
    main()