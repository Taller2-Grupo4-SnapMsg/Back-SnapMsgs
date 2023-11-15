"""
Queries for creating and deleting likes
"""
from typing import List
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import aliased

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.common_setup import *

# pylint: disable=C0114, W0401, W0614, E0401
from repository.errors import (
    DatabaseError,
    UserNotFound,
)

# pylint: disable=C0114, W0401, W0614, E0401
from repository.tables.posts import DeviceToken
from repository.tables.users import User

# ----- CREATE ------


def create_device_token(user_id: int, device_token: str):
    """
    Creates a device token for a user if it doesn't exist already
    """
    try:
        existing_token = (
            session.query(DeviceToken)
            .filter(
                DeviceToken.user_id == user_id, DeviceToken.device_token == device_token
            )
            .first()
        )
        if existing_token:
            return

        user = session.query(User).filter(User.id == user_id).first()
        if user is None:
            raise UserNotFound()

        new_device_token = DeviceToken(user_id, device_token)
        session.add(new_device_token)
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise DatabaseError from error


def get_device_tokens(users_id: List[int]):
    """
    Gets all device tokens for a list of users
    """
    dt_alias = aliased(DeviceToken)

    tokens = (
        session.query(
            DeviceToken.user_id, DeviceToken.device_token, DeviceToken.created_at
        )
        .join(dt_alias, DeviceToken.user_id == dt_alias.user_id)
        .filter(DeviceToken.user_id.in_(users_id))
        .group_by(DeviceToken.user_id, DeviceToken.device_token, DeviceToken.created_at)
        .all()
    )

    return tokens


def get_users_ids_by_emails(emails: List[str]):
    """
    Gets all users ids by a list of emails
    """
    users = session.query(User).filter(User.email.in_(emails)).all()
    return users


# ----- DELETE ------


def delete_device_token(user_id: int):
    """
    Deletes all device tokens for a user
    """
    try:
        device_tokens = (
            session.query(DeviceToken).filter(DeviceToken.user_id == user_id).first()
        )
        if device_tokens is None:
            raise UserNotFound()

        session.delete(device_tokens)
        # pylint: disable=R0801
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise DatabaseError from error
