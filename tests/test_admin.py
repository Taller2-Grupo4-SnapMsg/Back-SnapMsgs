"""
This module tests the functions from the controller_admin.py file
"""
from fastapi import Header

# pylint: disable=C0114, W0401, W0614, E0401, E0602, C0116
from control.controller_admin import *
from control.common_setup import *
from tests.mock_functions import *
from repository.tables.posts import *
from repository.errors import *


def test_get_service_health_and_description():
    """
    This function tests if you can get the health of the service.
    """
    response = get_service_health_and_description()
    assert response["status"] == "ok"
    assert (
        response["description"]
        == "SnapMsg's microservice handles everything related to the posts and their interactions"
    )


def test_get_posts_for_admin():
    """
    This function tests if you can get the posts for an admin.
    """
    user_1 = create_user(USERNAME_1, EMAIL_1, True)
    user_2 = create_user(USERNAME_2, EMAIL_2, True)
    post_1, _ = create_post(user_1.id)
    post_2, _ = create_post(user_2.id)
    post_3, _ = create_post(user_2.id)

    response = None

    try:

        def token_is_admin_mock(_: str = Header(None)):
            return True

        response = api_get_posts_for_admin(
            start=OFFSET_DEFAULT,
            ammount=AMOUNT_DEFAULT,
            is_admin=token_is_admin_mock(),
        )

        assert len(response) == 3
        assert response[0].post_id == post_3.post_id
        assert response[1].post_id == post_2.post_id
        assert response[2].post_id == post_1.post_id

    finally:
        delete_all()


def test_get_posts_for_admin_user_id():
    """
    This function tests if you can get the posts for a user for an admin.
    """
    user_1 = create_user(USERNAME_1, EMAIL_1, True)
    user_2 = create_user(USERNAME_2, EMAIL_2, True)
    create_post(user_1.id)
    create_post(user_2.id)
    create_post(user_2.id)

    response = None

    try:

        def token_is_admin_mock(_: str = Header(None)):
            return True

        response = api_get_posts_for_admin_user_id(
            email=user_1.email,
            start=OFFSET_DEFAULT,
            ammount=AMOUNT_DEFAULT,
            is_admin=token_is_admin_mock(),
        )

        assert len(response) == 1
        assert response[0].user_creator.id == user_1.id

    finally:
        delete_all()


def test_get_posts_for_admin_search():
    """
    This function tests if you can get the posts with the text passed by parameter.
    """
    user_1 = create_user(USERNAME_1, EMAIL_1, True)
    user_2 = create_user(USERNAME_2, EMAIL_2, True)
    create_post(user_2.id, content=":)")
    create_post(user_1.id, content="taller2")
    create_post(user_2.id, content="hi!")

    response = None

    try:

        def token_is_admin_mock(_: str = Header(None)):
            return True

        response = api_get_posts_for_admin_search(
            text="tall",
            offset=OFFSET_DEFAULT,
            amount=AMOUNT_DEFAULT,
            is_admin=token_is_admin_mock(),
        )

        assert len(response) == 1
        assert response[0].text == "taller2"

    finally:
        delete_all()
