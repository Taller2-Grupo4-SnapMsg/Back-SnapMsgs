# pylint: disable=R0801
"""
This module tests the function api_get_statistics from the controller_post.py file
"""
import json
from fastapi import Header

# pylint: disable=C0114, W0401, W0614, E0401, E0602, C0116
from control.controller_post import *
from control.common_setup import *
from tests.mock_functions import *
from repository.tables.posts import *
from repository.errors import *


def test_get_stadistics():
    """
    Tests the function api_get_statistics.
    """
    user_1 = create_user(USERNAME_1, EMAIL_1, True)
    user_2 = create_user(USERNAME_2, EMAIL_2, True)

    from_date = datetime.datetime.now()

    # user_1 makes 2 posts
    _, content_id_1 = create_post(user_1.id)
    _, content_id_2 = create_post(user_1.id)

    _, content_id_3 = create_post(user_2.id)

    # user 2 gives two likes to user_1 posts
    create_like(user_2.id, content_id_2)
    create_like(user_2.id, content_id_1)

    # user_1 makes 1 repost
    create_repost(user_1.id, user_2.id, content_id_3)

    # user_2 reposts user_1
    create_repost(user_2.id, user_1.id, content_id_1)

    try:

        def get_user_from_token_mock(_: str = Header(None)):
            return json.loads(generate_user_from_db(user_1).json())

        response = api_get_statistics(
            from_date_str=(from_date).strftime("%Y-%m-%d_%H:%M:%S"),
            to_date_str=(datetime.datetime.now() + datetime.timedelta(days=1)).strftime(
                "%Y-%m-%d_%H:%M:%S"
            ),
            user=get_user_from_token_mock(),
        )
        print(response)
        assert response.get("my_posts_count") == 2
        assert response.get("likes_count") == 2
        assert response.get("my_reposts_count") == 1
        assert response.get("others_reposts_count") == 1
    finally:
        delete_all()
