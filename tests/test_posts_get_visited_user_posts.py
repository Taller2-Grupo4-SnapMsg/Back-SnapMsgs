# pylint: disable=R0801
"""
This module tests the function get_posts_and_reposts_from_
user_visited from the controller_post.py file
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


def test_get_the_right_amount_posts_and_reposts_from_user_visited():
    """
    This function tests if you can get posts and reposts from a user.
    """
    user_visited = create_user(USERNAME_1, EMAIL_1, True)
    user_visitor = create_user(USERNAME_2, EMAIL_2, True)
    create_post(user_visited.id)
    create_post(user_visited.id)
    create_post(user_visited.id)

    try:

        def get_user_from_token_mock(_: str = Header(None)):
            return json.loads(generate_user_from_db(user_visitor).json())

        result = api_get_posts_and_reposts_from_user_visited(
            user_visited_email=user_visited.email,
            oldest_date_str=(
                datetime.datetime.now() + datetime.timedelta(days=1)
            ).strftime("%Y-%m-%d_%H:%M:%S"),
            amount=AMOUNT_DEFAULT,
            only_reposts=False,
            user=get_user_from_token_mock(),
        )

        assert len(result) == 3
    finally:
        delete_all()


def test_get_posts_if_the_user_is_private_and_i_dont_follow_them():
    """
    This function tests if you can get posts and reposts from a user.
    """
    user_visited = create_user(USERNAME_1, EMAIL_1, False)
    user_visitor = create_user(USERNAME_2, EMAIL_2, True)
    create_post(user_visited.id)

    try:

        def get_user_from_token_mock(_: str = Header(None)):
            return json.loads(generate_user_from_db(user_visitor).json())

        result = api_get_posts_and_reposts_from_user_visited(
            user_visited_email=user_visited.email,
            oldest_date_str=(
                datetime.datetime.now() + datetime.timedelta(days=1)
            ).strftime("%Y-%m-%d_%H:%M:%S"),
            amount=AMOUNT_DEFAULT,
            only_reposts=False,
            user=get_user_from_token_mock(),
        )

        assert len(result) == 0
    finally:
        delete_all()


def test_get_posts_if_the_user_is_private_and_i_follow_them():
    """
    This function tests if you can get posts and reposts from a user.
    """
    user_visited = create_user(USERNAME_1, EMAIL_1, False)
    user_visitor = create_user(USERNAME_2, EMAIL_2, True)
    create_follow(user_visitor.id, user_visited.id)
    create_post(user_visited.id)

    try:

        def get_user_from_token_mock(_: str = Header(None)):
            return json.loads(generate_user_from_db(user_visitor).json())

        result = api_get_posts_and_reposts_from_user_visited(
            user_visited_email=user_visited.email,
            oldest_date_str=(
                datetime.datetime.now() + datetime.timedelta(days=1)
            ).strftime("%Y-%m-%d_%H:%M:%S"),
            amount=AMOUNT_DEFAULT,
            only_reposts=False,
            user=get_user_from_token_mock(),
        )

        assert len(result) == 1
    finally:
        delete_all()


def test_get_only_the_ones_that_are_repost():
    """
    This function tests if you can get posts and reposts from a user.
    """
    user_visited = create_user(USERNAME_1, EMAIL_1, True)
    user_visitor = create_user(USERNAME_2, EMAIL_2, True)

    # El usuario visitado hace un respost de un post del usuario visitante
    _, content_id = create_post(user_visitor.id)
    create_repost(user_visited.id, user_visitor.id, content_id)

    # El usuario visitado crea un post
    _, content_id = create_post(user_visited.id)

    try:

        def get_user_from_token_mock(_: str = Header(None)):
            return json.loads(generate_user_from_db(user_visitor).json())

        result = api_get_posts_and_reposts_from_user_visited(
            user_visited_email=user_visited.email,
            oldest_date_str=(
                datetime.datetime.now() + datetime.timedelta(days=1)
            ).strftime("%Y-%m-%d_%H:%M:%S"),
            amount=AMOUNT_DEFAULT,
            only_reposts=True,
            user=get_user_from_token_mock(),
        )

        assert len(result) == 1
    finally:
        delete_all()


def test_get_amount_posts_from_user_visited():
    """
    This function tests if you can get amount posts from a user.
    """
    user_visited = create_user(USERNAME_1, EMAIL_1, True)
    user_visitor = create_user(USERNAME_2, EMAIL_2, True)

    # El usuario visitado hace un respost de un post del usuario visitante
    _, content_id = create_post(user_visitor.id)
    create_repost(user_visited.id, user_visitor.id, content_id)

    # El usuario visitado crea un post
    _, content_id = create_post(user_visited.id)

    try:

        def get_user_from_token_mock(_: str = Header(None)):
            return json.loads(generate_user_from_db(user_visitor).json())

        result = api_get_amount_posts_from_user_visited(
            user_visited_email=user_visited.email,
            user=get_user_from_token_mock(),
        )

        assert result == 1
    finally:
        delete_all()
