"""
This module tests the functions from the controller_trending_topic.py file
"""
import json
from fastapi import Header

# pylint: disable=C0114, W0401, W0614, E0401, E0602, C0116
from control.controller_trending_topic import *
from control.common_setup import *
from tests.mock_functions import *
from repository.tables.posts import *
from repository.errors import *


def test_trending_topics():
    """
    This function tests if you can get the trending topics.
    """
    user_1 = create_user(USERNAME_1, EMAIL_1, True)
    user_2 = create_user(USERNAME_2, EMAIL_2, True)
    create_post(user_1.id, hashtags=["#trending", "#topic", "#taller2"])
    create_post(user_2.id, hashtags=["#trending", "#taller2"])
    create_post(user_2.id, hashtags=["#taller2", "#hi!"])

    response = None

    try:

        def get_user_from_token_mock(_: str = Header(None)):
            return json.loads(generate_user_from_db(user_1).json())

        response = api_get_trending_topics(
            offset=OFFSET_DEFAULT,
            amount=2,
            days=DAYS_DEFAULT,
            user=get_user_from_token_mock(),
        )

        assert len(response) == 2
        assert response[0].trending_topic == "#taller2"
        assert response[0].number_of_posts == 3
        assert response[1].trending_topic == "#trending"
        assert response[1].number_of_posts == 2

    finally:
        delete_all()


def test_trending_topics_user_private():
    """
    This function tests if you can get the trending topics.
    """
    user_1 = create_user(USERNAME_1, EMAIL_1, False)
    user_2 = create_user(USERNAME_2, EMAIL_2, True)
    create_post(user_1.id, hashtags=["#trending", "#topic", "#taller2"])
    create_post(user_2.id, hashtags=["#taller2"])

    response = None

    try:

        def get_user_from_token_mock(_: str = Header(None)):
            return json.loads(generate_user_from_db(user_1).json())

        response = api_get_trending_topics(
            offset=OFFSET_DEFAULT,
            amount=2,
            days=DAYS_DEFAULT,
            user=get_user_from_token_mock(),
        )

        assert len(response) == 1
        assert response[0].trending_topic == "#taller2"
        assert response[0].number_of_posts == 1

    finally:
        delete_all()
