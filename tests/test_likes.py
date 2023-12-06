# pylint: disable=R0801
"""
This module tests the functions from the controller_like.py file
"""
import json
import pytest
from fastapi import Header

# pylint: disable=C0114, W0401, W0614, E0401, E0602, C0116
from control.controller_like import *
from control.common_setup import *
from tests.mock_functions import *
from repository.tables.posts import *
from repository.errors import *


def test_create_like_of_my_own_post():
    """
    Tests the function api_create_like.
    """
    # pylint disable=R0801
    user_1 = create_user(USERNAME_1, EMAIL_1, True)
    post_1, _ = create_post(user_1.id)

    try:

        def get_user_from_token_mock(_: str = Header(None)):
            return json.loads(generate_user_from_db(user_1).json())

        response = api_create_like(
            post_id=post_1.post_id,
            user=get_user_from_token_mock(),
        )
        assert response.get("message") == "Like created successfully"
    finally:
        delete_all()


def test_create_like_of_another_user_post():
    """
    Tests the function api_create_like.
    """
    user_1 = create_user(USERNAME_1, EMAIL_1, True)
    user_2 = create_user(USERNAME_2, EMAIL_2, True)
    post_1, _ = create_post(user_2.id)

    try:

        def get_user_from_token_mock(_: str = Header(None)):
            return json.loads(generate_user_from_db(user_1).json())

        response = api_create_like(
            post_id=post_1.post_id,
            user=get_user_from_token_mock(),
        )

        assert response.get("message") == "Like created successfully"
    finally:
        delete_all()


def test_create_like_of_a_post_that_does_not_exist():
    """
    Tests the function api_create_like.
    """
    user_1 = create_user(USERNAME_1, EMAIL_1, True)

    try:

        def get_user_from_token_mock(_: str = Header(None)):
            return json.loads(generate_user_from_db(user_1).json())

        with pytest.raises(HTTPException) as error_info:
            # pylint disable=R0801
            api_create_like(
                post_id=1,
                user=get_user_from_token_mock(),
            )
        error = error_info.value
        assert str(error.detail) == "Post not found"

    finally:
        delete_all()


def test_create_like_if_the_user_had_already_created_a_like_of_that_post():
    """
    Tests the function api_create_like.
    """
    user_1 = create_user(USERNAME_1, EMAIL_1, True)
    post_1, content_id = create_post(user_1.id)
    create_like(user_1.id, content_id)

    try:

        def get_user_from_token_mock(_: str = Header(None)):
            return json.loads(generate_user_from_db(user_1).json())

        with pytest.raises(HTTPException) as error_info:
            api_create_like(
                post_id=post_1.post_id,
                user=get_user_from_token_mock(),
            )
        error = error_info.value
        assert str(error.detail) == "Post doesnt exist or like already exists"

    finally:
        delete_all()


def test_delete_like():
    """
    Tests the function api_delete_like.
    """
    user_1 = create_user(USERNAME_1, EMAIL_1, True)
    post_1, content_id = create_post(user_1.id)
    create_like(user_1.id, content_id)
    try:

        def get_user_from_token_mock(_: str = Header(None)):
            return json.loads(generate_user_from_db(user_1).json())

        response = api_delete_like(
            post_id=post_1.post_id,
            user=get_user_from_token_mock(),
        )
        assert response.get("message") == "Like deleted successfully"
    finally:
        delete_all()


def test_delete_a_non_existent_like():
    """
    Tests the function api_delete_like.
    """
    user_1 = create_user(USERNAME_1, EMAIL_1, True)
    post_1, _ = create_post(user_1.id)

    try:

        def get_user_from_token_mock(_: str = Header(None)):
            return json.loads(generate_user_from_db(user_1).json())

        with pytest.raises(HTTPException) as error_info:
            api_delete_like(
                post_id=post_1.post_id,
                user=get_user_from_token_mock(),
            )
        error = error_info.value
        assert str(error.detail) == "Like not found"

    finally:
        delete_all()
