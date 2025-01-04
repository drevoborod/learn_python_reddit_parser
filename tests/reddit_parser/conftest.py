import pytest

from reddit_parser.searcher import TopUsersSearcher
from tests.mocks.api_mocks import MockRedditApi, MockRedditUser, MockRedditSubreddits
from tests.mocks.mock_data import REDDIT_SUBREDDITS_GET_NEW_1, REDDIT_SUBREDDITS_GET_COMMENTS_1


@pytest.fixture
def api_mock_positive() -> MockRedditApi:
    user_mock = MockRedditUser()
    subreddits_mock = MockRedditSubreddits(
        get_top_responses=[],
        get_new_responses=REDDIT_SUBREDDITS_GET_NEW_1,
        get_comments_responses=REDDIT_SUBREDDITS_GET_COMMENTS_1,
    )
    return MockRedditApi(user_mock=user_mock, subreddits_mock=subreddits_mock)


@pytest.fixture
def top_users_searcher_positive(api_mock_positive) -> TopUsersSearcher:
    return TopUsersSearcher(api_mock_positive)
