# pylint: disable=R0801
"""
This module tests the functions from the controller_repost.py file
"""
import json
import pytest
from fastapi import Header

# pylint: disable=C0114, W0401, W0614, E0401, E0602, C0116
from control.controller_repost import *
from control.common_setup import *
from tests.mock_functions import *
from repository.tables.posts import *
from repository.errors import *


def test_create_repost():
    """
    This function tests if you can create a repost.
    """
    user_1 = create_user(USERNAME_1, EMAIL_1, True)
    user_2 = create_user(USERNAME_2, EMAIL_2, True)
    post_1, _ = create_post(user_1.id)

    response = None

    try:

        def get_user_from_token_mock(_: str = Header(None)):
            return json.loads(generate_user_from_db(user_2).json())

        response = api_create_repost(
            post_id=post_1.post_id,
            user=get_user_from_token_mock(),
        )

        assert response.get("message") == "Repost created successfully"
    finally:
        delete_all()


def test_create_repost_from_a_private_user():
    """
    This function tests if you can create a repost,
    if the user is private, an exception is thrown.
    """
    user_1 = create_user(USERNAME_1, EMAIL_1, False)
    user_2 = create_user(USERNAME_2, EMAIL_2, True)
    post_1, _ = create_post(user_1.id)

    try:

        def get_user_from_token_mock(_: str = Header(None)):
            return json.loads(generate_user_from_db(user_2).json())

        with pytest.raises(HTTPException) as error_info:
            api_create_repost(
                post_id=post_1.post_id,
                user=get_user_from_token_mock(),
            )

        error = error_info.value
        assert str(error.detail) == "User doesnt have permissions to do that action."
    finally:
        delete_all()


def test_user_tries_to_repost_if_he_already_reposted():
    """
    This function tests if you can create a repost
    if the repost already exists.
    """
    user_1 = create_user(USERNAME_1, EMAIL_1, True)
    user_2 = create_user(USERNAME_2, EMAIL_2, True)

    # El usuario 2 hace un repost del post del usuario 1
    post_1, content_id = create_post(user_1.id)
    create_repost(user_2.id, user_1.id, content_id)

    try:

        def get_user_from_token_mock(_: str = Header(None)):
            return json.loads(generate_user_from_db(user_2).json())

        with pytest.raises(HTTPException) as error_info:
            api_create_repost(
                post_id=post_1.post_id,
                user=get_user_from_token_mock(),
            )

        error = error_info.value
        assert str(error.detail) == "User already reposted that post."

    finally:
        delete_all()


def test_delete_repost():
    """
    Tests the function api_delete_respost_from_post.
    """
    user_1 = create_user(USERNAME_1, EMAIL_1, True)
    user_2 = create_user(USERNAME_2, EMAIL_2, True)
    post_1, content_id = create_post(user_2.id)
    create_repost(user_1.id, user_2.id, content_id)
    try:

        def get_user_from_token_mock(_: str = Header(None)):
            return json.loads(generate_user_from_db(user_1).json())

        response = api_delete_respost_from_post(
            post_id=post_1.post_id,
            user=get_user_from_token_mock(),
        )
        assert response.get("message") == "Repost deleted successfully"
    finally:
        delete_all()


def test_delete_a_non_existent_repost():
    """
    Tests the function api_delete_respost_from_post.
    """
    user_1 = create_user(USERNAME_1, EMAIL_1, True)
    user_2 = create_user(USERNAME_2, EMAIL_2, True)
    post_1, _ = create_post(user_2.id)

    try:

        def get_user_from_token_mock(_: str = Header(None)):
            return json.loads(generate_user_from_db(user_1).json())

        with pytest.raises(HTTPException) as error_info:
            api_delete_respost_from_post(
                post_id=post_1.post_id,
                user=get_user_from_token_mock(),
            )
        error = error_info.value
        assert str(error.detail) == "Post not found"

    finally:
        delete_all()
