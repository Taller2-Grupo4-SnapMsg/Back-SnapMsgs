"""
This module tests the function create_post from the controller_post.py file
"""
import json
import pytest
from fastapi import Header

# pylint: disable=C0114, W0401, W0614, E0401, E0602, C0116
from control.controller_post import *
from control.common_setup import *
from tests.mock_functions import *
from repository.tables.posts import *
from repository.errors import *


def test_create_post():
    """
    This function tests if you can create a post.
    """
    user_1 = create_user(USERNAME_1, EMAIL_1, True)

    response = None

    try:

        def get_user_from_token_mock(_: str = Header(None)):
            return json.loads(generate_user_from_db(user_1).json())

        response = api_create_post(
            post=PostCreateRequest(
                content=TEXT,
                image=IMAGE,
                hashtags=HASHTAGS,
                mentions=MENTIONS,
            ),
            user=get_user_from_token_mock(),
        )

        assert response.get("post_id") is not None
        assert response.get("message") == "Post created successfully"
    finally:
        post_delete_by_id(response.get("post_id"))
        user_delete(user_1)


def test_create_a_post_without_text_and_image():
    """
    This function tests if you can create a post.
    """
    user_1 = create_user(USERNAME_1, EMAIL_1, True)

    response = None

    try:

        def get_user_from_token_mock(_: str = Header(None)):
            return json.loads(generate_user_from_db(user_1).json())

        with pytest.raises(HTTPException) as error_info:
            response = api_create_post(
                post=PostCreateRequest(
                    content="",
                    image="",
                    hashtags=HASHTAGS,
                    mentions=MENTIONS,
                ),
                user=get_user_from_token_mock(),
            )

        error = error_info.value
        assert str(error.detail) == "Both text and image are empty."
    finally:
        if response and response.get("post_id"):
            post_delete_by_id(response.get("post_id"))
        user_delete(user_1)


def test_create_a_post_with_text_of_more_than_1000_characters():
    """
    This function tests if you can create a post.
    """
    user_1 = create_user(USERNAME_1, EMAIL_1, True)

    response = None

    try:

        def get_user_from_token_mock(_: str = Header(None)):
            return json.loads(generate_user_from_db(user_1).json())

        with pytest.raises(HTTPException) as error_info:
            response = api_create_post(
                post=PostCreateRequest(
                    content=LONG_TEXT,
                    image=IMAGE,
                    hashtags=HASHTAGS,
                    mentions=MENTIONS,
                ),
                user=get_user_from_token_mock(),
            )

        error = error_info.value
        assert str(error.detail) == "Text exceeds maximum length of 1000 characters."
    finally:
        if response and response.get("post_id"):
            post_delete_by_id(response.get("post_id"))
        user_delete(user_1)
