# pylint: skip-file
"""
Functions to mock backend-user behaviour.
Normally the user would have to create their account and then navigate.
Here I have funcitons that create the user with my parameters.
No checks of verifications are made.
"""

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.common_setup import *
from repository.tables.users import User, Following, Interests
import datetime


def user_save(username, surname, name, password, email, is_public):
    new_user = User(
        username=username,
        surname=surname,
        name=name,
        password=password,
        email=email,
        date_of_birth=datetime.datetime(1990, 1, 1),
        bio="This is a bio.",
        avatar="path_to_avatar",
        admin=False,
        location="Some Location",
        blocked=False,
        is_public=is_public,
    )

    session.add(new_user)
    session.commit()

    return new_user


def user_delete(user):
    session.delete(user)
    session.commit()


def follow_save(user_id, following_id):
    new_follow = Following(
        user_id=user_id,
        following_id=following_id,
    )

    session.add(new_follow)
    session.commit()

    return new_follow


def interest_save(user_id, interest):
    new_interest = Interests(
        user_id=user_id,
        interest=interest,
    )

    session.add(new_interest)
    session.commit()

    return new_interest
