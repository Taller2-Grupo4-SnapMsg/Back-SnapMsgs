import json
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from control.controller_post import api_create_post, api_get_post_by_id
from control.common_setup import *

from control.app import app
import datetime
import pytest

# pylint: disable=C0114, W0401, W0614, E0401, E0602, C0116
from tests.mock_functions import *
from repository.tables.posts import *
from fastapi import Header


def test_get_post_by_id():
    """
    This function tests if you can get a post by id.
    """
    user_1 = create_user(USERNAME_1, EMAIL_1, True)

    post_1 = create_post(
        TEXT,
        IMAGE,
        HASHTAGS,
        MENTIONS,
        user_1.id,
        user_1.id,
    )

    def get_user_from_token_mock(token: str = Header(None)):
        return json.loads(generate_user_from_db(user_1).json())

    result = api_get_post_by_id(
        post_id=post_1.post_id,
        token="fake_token",
        get_user_func=get_user_from_token_mock,
    )

    assert result[0].post_id == post_1.post_id
    assert result[0].user_creator.id == post_1.user_creator_id
    assert result[0].user_poster.id == post_1.user_poster_id
    assert result[0].text == TEXT
    assert result[0].image == IMAGE

    post_delete(post_1)
    user_delete(user_1)
