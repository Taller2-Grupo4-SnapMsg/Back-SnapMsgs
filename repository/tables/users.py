# users.py

"""
This module represents the tables on the database of the users' microservice 
"""

import datetime
from sqlalchemy import Column, Integer
from sqlalchemy import String, DateTime
from sqlalchemy import Boolean, ForeignKey
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import declarative_base

Base = declarative_base()


def create_users_foreign_key():
    """
    This function creates a column with user_id as a foregin key.
    """
    return Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
    )


# pylint: disable=too-few-public-methods
# pylint: disable=too-many-instance-attributes
class User(Base):
    """
    Class that represents the user class on the database.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(100), unique=True, nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    name = Column(String(50), nullable=False)
    surname = Column(String(50), nullable=False)
    password = Column(String(200), nullable=False)
    admin = Column(Boolean, default=False)
    date_of_birth = Column(DateTime, nullable=False)
    bio = Column(String(500), nullable=False)
    avatar = Column(String(), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    location = Column(String(100), nullable=False)
    blocked = Column(Boolean, nullable=False, default=False)
    is_public = Column(Boolean, default=True, nullable=False)

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        username,
        surname,
        name,
        password,
        email,
        date_of_birth=datetime.datetime(666, 6, 6),
        bio="",
        avatar="",
        admin=False,
        location="",
        blocked=False,
        is_public=True,
    ):  # This is for the repetive nature of this code and users.save()
        # pylint: disable=R0801
        self.username = username
        self.surname = surname
        self.name = name
        self.password = password
        self.email = email
        self.date_of_birth = date_of_birth
        self.bio = bio
        self.avatar = avatar
        self.admin = admin
        self.location = location
        self.blocked = blocked
        self.is_public = is_public


class Following(Base):
    """
    Class that represents the following relation on the data base.
    """

    __tablename__ = "following"

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
    )

    following_id = create_users_foreign_key()
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    _table_args__ = (UniqueConstraint("user_id", "following_id"),)

    # pylint: disable=too-many-arguments
    def __init__(self, user_id, following_id):
        self.user_id = user_id
        self.following_id = following_id


class Interests(Base):
    """
    Class that represents the interests table of users
    """

    __tablename__ = "interests"

    # We disable duplicate code here since it is a table and the
    # foreign key is the same in all tables
    # pylint: disable=R0801
    user_id = create_users_foreign_key()

    interest = Column(String(75), nullable=False, primary_key=True)

    _table_args__ = (UniqueConstraint("user_id", "interest"),)

    def __init__(self, user_id, interest):
        self.user_id = user_id
        self.interest = interest
