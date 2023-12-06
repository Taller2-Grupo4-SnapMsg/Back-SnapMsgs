# pylint: disable=R0801
"""
This module tests the function api_get_post_by_id from the controller_post.py file
"""
import json
from fastapi import Header

# pylint: disable=C0114, W0401, W0614, E0401, E0602, C0116
from control.controller_post import *
from control.common_setup import *
from tests.mock_functions import *
from repository.tables.posts import *
from repository.errors import *


def test_get_post_by_id():
    """
    This function tests if you can get a post by id.
    """
    user_1 = create_user(USERNAME_1, EMAIL_1, True)
    post_1, _ = create_post(user_1.id)

    try:

        def get_user_from_token_mock(_: str = Header(None)):
            return json.loads(generate_user_from_db(user_1).json())

        result = api_get_post_by_id(
            post_id=post_1.post_id,
            user=get_user_from_token_mock(),
        )

        assert result[0].post_id == post_1.post_id
    finally:
        delete_all()
