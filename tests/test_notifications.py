"""
This module tests the functions from the controller_notifications.py file
"""
import json
from fastapi import Header

# pylint: disable=C0114, W0401, W0614, E0401, E0602, C0116
from control.controller_notifications import *
from control.common_setup import *
from tests.mock_functions import *
from repository.tables.posts import *
from repository.errors import *


def test_save_device_token():
    """
    Tests the function api_save_device_token.
    """
    user_1 = create_user(USERNAME_1, EMAIL_1, True)
    device_token = DEVICE_TOKEN
    try:

        def get_user_from_token_mock(_: str = Header(None)):
            return json.loads(generate_user_from_db(user_1).json())

        response = api_save_device_token(
            device_token=device_token,
            user=get_user_from_token_mock(),
        )
        assert response.get("mensaje") == "token stored successfully"
    finally:
        delete_all()


def test_delete_device_token():
    """
    Tests the function api_delete_device_token.
    """
    user_1 = create_user(USERNAME_1, EMAIL_1, True)
    device_token = DEVICE_TOKEN
    try:

        def get_user_from_token_mock(_: str = Header(None)):
            return json.loads(generate_user_from_db(user_1).json())

        api_save_device_token(
            device_token=device_token,
            user=get_user_from_token_mock(),
        )

        response = api_delete_device_token(
            user=get_user_from_token_mock(),
        )
        assert response.get("mensaje") == "token delete successfully"
    finally:
        delete_all()


def test_send_notification():
    """
    Tests the function api_send_notification.
    """
    user_1 = create_user(USERNAME_1, EMAIL_1, True)
    device_token = DEVICE_TOKEN
    save_device_token(user_1.id, DEVICE_TOKEN)
    try:

        def get_user_from_token_mock(_: str = Header(None)):
            return json.loads(generate_user_from_db(user_1).json())

        api_save_device_token(
            device_token=device_token,
            user=get_user_from_token_mock(),
        )

        response = api_send_notificacion(
            notificacion_request=NotificationRequest(
                user_emails_that_receive=[user_1.email],
                title=TITLE,
                body=BODY,
                data=DATA,
            ),
            _=get_user_from_token_mock(),
        )
        assert response.get("mensaje") == "Notification sent successfully"
    finally:
        delete_all()
