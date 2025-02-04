class TestTopUsersSearcher:
    def test_get_positive(self, top_users_searcher_positive):
        result = top_users_searcher_positive.process("abrakadabra")
        assert result == {
            'top_users_by_comments': ['random_author_013: 10', 'random_author_001: 8', 'random_author_012: 8',
                                      'random_author_007: 7', 'random_author_011: 7', 'random_author_017: 7',
                                      'random_author_018: 7', 'random_author_008: 6', 'random_author_003: 5',
                                      'random_author_019: 5', 'random_author_006: 4', 'random_author_016: 4',
                                      'random_author_010: 3', 'random_author_000: 2', 'random_author_004: 2',
                                      'random_author_005: 2', 'random_author_015: 2', 'random_author_002: 1',
                                      'random_author_009: 1', 'random_author_014: 1'],
            'top_users_by_posts': ['random_author_003: 3', 'random_author_002: 2', 'random_author_001: 2',
                                   'random_author_000: 2', 'random_author_019: 1', 'random_author_018: 1',
                                   'random_author_017: 1', 'random_author_016: 1', 'random_author_015: 1',
                                   'random_author_014: 1', 'random_author_013: 1', 'random_author_012: 1',
                                   'random_author_011: 1', 'random_author_010: 1', 'random_author_009: 1',
                                   'random_author_008: 1', 'random_author_007: 1', 'random_author_006: 1',
                                   'random_author_005: 1', 'random_author_004: 1']}
