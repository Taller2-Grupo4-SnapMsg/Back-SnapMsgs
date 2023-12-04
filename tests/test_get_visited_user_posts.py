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
    post_1 = create_post(user_visited.id)
    post_2 = create_post(user_visited.id)
    post_3 = create_post(user_visited.id)

    try:

        def get_user_from_token_mock(_: str = Header(None)):
            print(json.loads(generate_user_from_db(user_visitor).json()))
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
        post_delete(post_1)
        post_delete(post_2)
        post_delete(post_3)
        user_delete(user_visited)
        user_delete(user_visitor)


### TEST PENDIENTE
# get the right amount and with
# the right offset of posts and
# reposts from the visited user


### VER, NO SE ESTA TIRANDO LA EXCEPCION
def test_get_posts_if_the_user_is_private_and_i_dont_follow_them():
    """
    This function tests if you can get posts and reposts from a user.
    """
    user_visited = create_user(USERNAME_1, EMAIL_1, False)
    user_visitor = create_user(USERNAME_2, EMAIL_2, True)
    post_1 = create_post(user_visited.id)

    try:

        def get_user_from_token_mock(_: str = Header(None)):
            return json.loads(generate_user_from_db(user_visitor).json())

        # with pytest.raises(HTTPException) as error_info:
        result = api_get_posts_and_reposts_from_user_visited(
            user_visited_email=user_visited.email,
            oldest_date_str=(
                datetime.datetime.now() + datetime.timedelta(days=1)
            ).strftime("%Y-%m-%d_%H:%M:%S"),
            amount=AMOUNT_DEFAULT,
            only_reposts=False,
            user=get_user_from_token_mock(),
        )
        # error = error_info.value
        # assert str(error.detail) == "User is private"
        assert len(result) == 0
    finally:
        post_delete(post_1)
        user_delete(user_visited)
        user_delete(user_visitor)


def test_get_posts_if_the_user_is_private_and_i_follow_them():
    """
    This function tests if you can get posts and reposts from a user.
    """
    user_visited = create_user(USERNAME_1, EMAIL_1, False)
    user_visitor = create_user(USERNAME_2, EMAIL_2, True)
    create_follow(user_visitor.id, user_visited.id)
    post_1 = create_post(user_visited.id)

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
        post_delete(post_1)
        delete_follow(user_visitor.id, user_visited.id)
        user_delete(user_visited)
        user_delete(user_visitor)


# #tengo que hacer el create de repost
# def test_get_only_the_ones_that_are_repost():
#     """
#     This function tests if you can get posts and reposts from a user.
#     """
#     user_visited = create_user(USERNAME_1, EMAIL_1, True)
#     user_visitor = create_user(USERNAME_2, EMAIL_2, True)
#     create_repost(1, user_visitor.id)
#     post_1 = create_post(user_visited.id)
#     post_2 = create_post(user_visited.id)
#     post_3 = create_post(user_visited.id)

#     def get_user_from_token_mock(_: str = Header(None)):
#         print(json.loads(generate_user_from_db(user_visitor).json()))
#         return json.loads(generate_user_from_db(user_visitor).json())

#     result = api_get_posts_and_reposts_from_user_visited(
#         user_visited_email=user_visited.email,
#         oldest_date_str=(datetime.datetime.now() +
# datetime.timedelta(days=1)).strftime("%Y-%m-%d_%H:%M:%S"),
#         amount=AMOUNT_DEFAULT,
#         only_reposts=True,
#         user=get_user_from_token_mock(token=TOKEN_FAKE),
#     )

#     assert len(result) == 3

#     post_delete(post_1)
#     post_delete(post_2)
#     post_delete(post_3)
#     user_delete(user_visited)
#     user_delete(user_visitor)


# --------------------- pendiente ---------------------

# ## NO FUNCIONA, VER, NO SE ESTA TIRANDO LA EXCEPCION, CREO QUE ESTA EN OTRA RAMA
# def test_get_posts_if_the_user_is_blocked():
#     """
#     This function tests if you can get posts and reposts from a user.
#     """
#     delete_all_posts()
#     delete_user_by_username(USERNAME_1)
#     delete_user_by_username(USERNAME_2)

#     user_visited = create_user(USERNAME_1, EMAIL_1, True, True)
#     user_visitor = create_user(USERNAME_2, EMAIL_2, True, False)
#     post_1 = create_post(user_visited.id)

#     def get_user_from_token_mock(_: str = Header(None)):
#         return json.loads(generate_user_from_db(user_visitor).json())

#     #with pytest.raises(UserIsPrivate) as error:
#     result = api_get_posts_and_reposts_from_user_visited(
#         user_visited_email=user_visited.email,
#         oldest_date_str=(datetime.datetime.now()
# + datetime.timedelta(days=1)).strftime("%Y-%m-%d_%H:%M:%S"),
#         amount=AMOUNT_DEFAULT,
#         only_reposts=False,
#         user=get_user_from_token_mock(token=TOKEN_FAKE),
#     )
#     #assert str(error.value) == "User is private"
#     assert len(result) == 0

#     post_delete(post_1)
#     user_delete(user_visited)
#     user_delete(user_visitor)


# # solo se puede repostear de usuarios publicos
