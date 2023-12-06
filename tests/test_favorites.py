# pylint: disable=R0801
"""
This module tests the functions from the controller_favorite.py file
"""
import json
import pytest
from fastapi import Header

# pylint: disable=C0114, W0401, W0614, E0401, E0602, C0116
from control.controller_favorite import *
from control.common_setup import *
from tests.mock_functions import *
from repository.tables.posts import *
from repository.errors import *


def test_create_favorite_of_my_own_post():
    """
    Tests the function api_create_favorite.
    """
    # pylint disable=R0801
    user_1 = create_user(USERNAME_1, EMAIL_1, True)
    post_1, _ = create_post(user_1.id)

    try:

        def get_user_from_token_mock(_: str = Header(None)):
            return json.loads(generate_user_from_db(user_1).json())

        response = api_create_favorite(
            post_id=post_1.post_id,
            user=get_user_from_token_mock(),
        )
        assert response.get("message") == "Favorite created successfully"
    finally:
        delete_all()


def test_create_favorite_of_another_user_post():
    """
    Tests the function api_create_favorite.
    """
    user_1 = create_user(USERNAME_1, EMAIL_1, True)
    user_2 = create_user(USERNAME_2, EMAIL_2, True)
    post_1, _ = create_post(user_2.id)

    try:

        def get_user_from_token_mock(_: str = Header(None)):
            return json.loads(generate_user_from_db(user_1).json())

        response = api_create_favorite(
            post_id=post_1.post_id,
            user=get_user_from_token_mock(),
        )

        assert response.get("message") == "Favorite created successfully"
    finally:
        delete_all()


def test_create_favorite_of_a_post_that_does_not_exist():
    """
    Tests the function api_create_favorite.
    """
    user_1 = create_user(USERNAME_1, EMAIL_1, True)

    try:

        def get_user_from_token_mock(_: str = Header(None)):
            return json.loads(generate_user_from_db(user_1).json())

        with pytest.raises(HTTPException) as error_info:
            # pylint disable=R0801
            api_create_favorite(
                post_id=1,
                user=get_user_from_token_mock(),
            )
        error = error_info.value
        assert str(error.detail) == "Post not found"

    finally:
        delete_all()


def test_create_favorite_if_the_user_had_already_created_a_favorite_of_that_post():
    """
    Tests the function api_create_favorite.
    """
    user_1 = create_user(USERNAME_1, EMAIL_1, True)
    post_1, content_id = create_post(user_1.id)
    create_favorite(user_1.id, content_id)

    try:

        def get_user_from_token_mock(_: str = Header(None)):
            return json.loads(generate_user_from_db(user_1).json())

        with pytest.raises(HTTPException) as error_info:
            api_create_favorite(
                post_id=post_1.post_id,
                user=get_user_from_token_mock(),
            )
        error = error_info.value
        assert str(error.detail) == "Post doesnt exist or favorite already exists"

    finally:
        delete_all()


def test_delete_favorite():
    """
    Tests the function api_delete_favorite.
    """
    user_1 = create_user(USERNAME_1, EMAIL_1, True)
    post_1, content_id = create_post(user_1.id)
    create_favorite(user_1.id, content_id)
    try:

        def get_user_from_token_mock(_: str = Header(None)):
            return json.loads(generate_user_from_db(user_1).json())

        response = api_delete_favorite(
            post_id=post_1.post_id,
            user=get_user_from_token_mock(),
        )
        assert response.get("message") == "Favorite deleted successfully"
    finally:
        delete_all()


def test_delete_a_non_existent_favorite():
    """
    Tests the function api_delete_favorite.
    """
    user_1 = create_user(USERNAME_1, EMAIL_1, True)
    post_1, _ = create_post(user_1.id)

    try:

        def get_user_from_token_mock(_: str = Header(None)):
            return json.loads(generate_user_from_db(user_1).json())

        with pytest.raises(HTTPException) as error_info:
            api_delete_favorite(
                post_id=post_1.post_id,
                user=get_user_from_token_mock(),
            )
        error = error_info.value
        assert str(error.detail) == "Favorite not found"

    finally:
        delete_all()


def test_the_user_gets_his_favorite_posts():
    """
    This function tests if you can get posts and reposts from a user.
    Three posts are created and user_1 favorites two posts. One is from
    the user and the other is not, it is expected to return two posts
    """
    user_1 = create_user(USERNAME_1, EMAIL_1, True)
    user_2 = create_user(USERNAME_2, EMAIL_2, True)
    post_1, content_id_1 = create_post(user_1.id)
    post_2, content_id_2 = create_post(user_2.id)
    create_post(user_2.id)
    create_favorite(user_1.id, content_id_1)
    create_favorite(user_1.id, content_id_2)

    try:

        def get_user_from_token_mock(_: str = Header(None)):
            return json.loads(generate_user_from_db(user_1).json())

        result = api_get_favorites_from_user_visited(
            user_visited_email=user_1.email,
            oldest_date_str=(
                datetime.datetime.now() + datetime.timedelta(days=1)
            ).strftime("%Y-%m-%d_%H:%M:%S"),
            amount=AMOUNT_DEFAULT,
            user=get_user_from_token_mock(),
        )

        assert len(result) == 2
        assert result[0].post_id == post_2.post_id
        assert result[1].post_id == post_1.post_id

    finally:
        delete_all()


def test_the_user_gets_the_favorites_of_another_user():
    """
    This function tests if you can get favorites posts from a user.
    """
    user_1 = create_user(USERNAME_1, EMAIL_1, True)
    user_2 = create_user(USERNAME_2, EMAIL_2, True)
    post_1, content_id_1 = create_post(user_1.id)
    post_2, content_id_2 = create_post(user_2.id)
    create_post(user_2.id)
    create_favorite(user_1.id, content_id_1)
    create_favorite(user_1.id, content_id_2)

    try:

        def get_user_from_token_mock(_: str = Header(None)):
            return json.loads(generate_user_from_db(user_2).json())

        result = api_get_favorites_from_user_visited(
            user_visited_email=user_1.email,
            oldest_date_str=(
                datetime.datetime.now() + datetime.timedelta(days=1)
            ).strftime("%Y-%m-%d_%H:%M:%S"),
            amount=AMOUNT_DEFAULT,
            user=get_user_from_token_mock(),
        )

        assert len(result) == 2
        assert result[0].post_id == post_2.post_id
        assert result[1].post_id == post_1.post_id

    finally:
        delete_all()


def test_get_the_favorites_if_the_user_is_private_and_i_dont_follow_them():
    """
    This function tests if you can get favorites posts from a user.
    """
    user_visited = create_user(USERNAME_1, EMAIL_1, False)
    user_visitor = create_user(USERNAME_2, EMAIL_2, True)
    _, content_id_1 = create_post(user_visited.id)
    create_favorite(user_visited.id, content_id_1)

    try:

        def get_user_from_token_mock(_: str = Header(None)):
            return json.loads(generate_user_from_db(user_visitor).json())

        result = api_get_favorites_from_user_visited(
            user_visited_email=user_visited.email,
            oldest_date_str=(
                datetime.datetime.now() + datetime.timedelta(days=1)
            ).strftime("%Y-%m-%d_%H:%M:%S"),
            amount=AMOUNT_DEFAULT,
            user=get_user_from_token_mock(),
        )

        assert len(result) == 0
    finally:
        delete_all()


def test_get_the_favorites_if_the_user_is_private_and_i_follow_them():
    """
    This function tests if you can get posts from a user.
    """
    user_visited = create_user(USERNAME_1, EMAIL_1, False)
    user_visitor = create_user(USERNAME_2, EMAIL_2, True)
    create_follow(user_visitor.id, user_visited.id)
    post_1, content_id_1 = create_post(user_visited.id)
    create_favorite(user_visited.id, content_id_1)

    try:

        def get_user_from_token_mock(_: str = Header(None)):
            return json.loads(generate_user_from_db(user_visitor).json())

        # pylint disable=R0801
        result = api_get_favorites_from_user_visited(
            user_visited_email=user_visited.email,
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
