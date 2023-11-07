"""
Queries for creating and deleting likes
"""
from typing import List
from sqlalchemy.exc import IntegrityError

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
    Creates a device token for a user
    """
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if user is None:
            raise UserNotFound()
        device_token = DeviceToken(user_id, device_token)
        session.add(device_token)
        # pylint: disable=R0801
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise DatabaseError from error


def get_device_tokens(users_id: List[int]):
    """
    Gets all device tokens for a list of users
    """
    tokens = session.query(DeviceToken).filter(DeviceToken.user_id.in_(users_id)).all()
    return tokens


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
