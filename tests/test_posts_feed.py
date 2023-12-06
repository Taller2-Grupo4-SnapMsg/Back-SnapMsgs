# pylint: disable=R0801
"""
This module tests the function api_get_feed from the controller_post.py file
"""
import datetime
import json
from fastapi import Header

# pylint: disable=C0114, W0401, W0614, E0401, E0602, C0116
from control.controller_post import *
from control.common_setup import *
from tests.mock_functions import *
from repository.tables.posts import *
from repository.errors import *


def test_get_the_posts_for_a_user_feed_returns_my_posts_and_those_of_the_user_i_follow():
    """
    This function tests if a user follows others their posts are returned.
    """
    user_1 = create_user(USERNAME_1, EMAIL_1, True)
    user_2 = create_user(USERNAME_2, EMAIL_2, True)

    create_follow(user_1.id, user_2.id)

    post_1, content_id_1 = create_post(user_1.id)
    post_2, _ = create_post(user_2.id)
    repost_1 = create_repost(user_2.id, user_1.id, content_id_1)

    try:

        def get_user_from_token_mock(_: str = Header(None)):
            return json.loads(generate_user_from_db(user_1).json())

        result = api_get_feed(
            oldest_date_str=(
                datetime.datetime.now() + datetime.timedelta(days=1)
            ).strftime("%Y-%m-%d_%H:%M:%S"),
            amount=AMOUNT_DEFAULT,
            user=get_user_from_token_mock(),
        )

        assert len(result) == 3
        assert result[0].post_id == repost_1.post_id
        assert result[1].post_id == post_2.post_id
        assert result[2].post_id == post_1.post_id

    finally:
        delete_all()


def test_get_posts_feed_if_user_is_private_and_i_dont_follow():
    """
    This function tests if a user follows others their posts are returned.
    """
    user_1 = create_user(USERNAME_1, EMAIL_1, True)
    user_2 = create_user(USERNAME_2, EMAIL_2, False)

    post_1, content_id_1 = create_post(user_1.id)
    create_post(user_2.id)
    create_repost(user_2.id, user_1.id, content_id_1)

    try:

        def get_user_from_token_mock(_: str = Header(None)):
            return json.loads(generate_user_from_db(user_1).json())

        result = api_get_feed(
            oldest_date_str=(
                datetime.datetime.now() + datetime.timedelta(days=1)
            ).strftime("%Y-%m-%d_%H:%M:%S"),
            amount=AMOUNT_DEFAULT,
            user=get_user_from_token_mock(),
        )

        assert len(result) == 1
        assert result[0].post_id == post_1.post_id

    finally:
        delete_all()


def test_get_posts_feed_if_the_user_follows_the_other_user_and_this_is_private():
    """
    This function tests if a user follows others their posts are returned.
    """
    user_1 = create_user(USERNAME_1, EMAIL_1, True)
    user_2 = create_user(USERNAME_2, EMAIL_2, False)

    create_follow(user_1.id, user_2.id)

    post_1, content_id_1 = create_post(user_1.id)
    post_2, _ = create_post(user_2.id)
    repost_1 = create_repost(user_2.id, user_1.id, content_id_1)

    try:

        def get_user_from_token_mock(_: str = Header(None)):
            return json.loads(generate_user_from_db(user_1).json())

        result = api_get_feed(
            oldest_date_str=(
                datetime.datetime.now() + datetime.timedelta(days=1)
            ).strftime("%Y-%m-%d_%H:%M:%S"),
            amount=AMOUNT_DEFAULT,
            user=get_user_from_token_mock(),
        )

        assert len(result) == 3
        assert result[0].post_id == repost_1.post_id
        assert result[1].post_id == post_2.post_id
        assert result[2].post_id == post_1.post_id

    finally:
        delete_all()


def test_get_posts_feed_if_user_is_public_i_dont_follow_and_match_my_interests():
    """
    This function tests if a user follows others their posts are returned.
    """
    user_1 = create_user(USERNAME_1, EMAIL_1, True)
    create_interest(user_1.id, INTEREST_1)
    create_interest(user_1.id, INTEREST_2)

    user_2 = create_user(USERNAME_2, EMAIL_2, True)

    post_1, _ = create_post(user_2.id, hashtags=[INTEREST_1])
    create_post(user_2.id)
    post_3, _ = create_post(user_2.id, hashtags=[INTEREST_2])

    try:

        def get_user_from_token_mock(_: str = Header(None)):
            return json.loads(generate_user_from_db(user_1).json())

        result = api_get_feed(
            oldest_date_str=(
                datetime.datetime.now() + datetime.timedelta(days=1)
            ).strftime("%Y-%m-%d_%H:%M:%S"),
            amount=AMOUNT_DEFAULT,
            user=get_user_from_token_mock(),
        )

        print(result)
        assert len(result) == 2
        assert result[0].post_id == post_3.post_id
        assert result[1].post_id == post_1.post_id

    finally:
        delete_all()
