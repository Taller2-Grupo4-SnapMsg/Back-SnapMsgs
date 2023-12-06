# pylint: disable=R0801
"""
This module tests the function api_get_posts_by_hashtags from the controller_post.py file
"""
import json
from fastapi import Header

# pylint: disable=C0114, W0401, W0614, E0401, E0602, C0116
from control.controller_post import *
from control.common_setup import *
from tests.mock_functions import *
from repository.tables.posts import *
from repository.errors import *


def test_get_posts_by_hashtags():
    """
    This function tests if you can get a post by hashtags.
    """
    user_1 = create_user(USERNAME_1, EMAIL_1, True)
    user_2 = create_user(USERNAME_2, EMAIL_2, True)

    create_post(user_1.id, hashtags=[HASHTAG_1, HASHTAG_2])
    create_post(user_2.id, hashtags=[HASHTAG_1])
    create_post(user_2.id, hashtags=[HASHTAG_2])

    try:

        def get_user_from_token_mock(_: str = Header(None)):
            return json.loads(generate_user_from_db(user_1).json())

        result = api_get_posts_by_hashtags(
            hashtags=HASHTAG_2,
            offset=OFFSET_DEFAULT,
            amount=AMOUNT_DEFAULT,
            user=get_user_from_token_mock(),
        )

        assert len(result) == 2
    finally:
        delete_all()
