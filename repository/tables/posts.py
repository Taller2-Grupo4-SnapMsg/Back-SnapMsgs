# tables.py

"""
This module represents the tables on the database of the users' microservice 
"""

import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, UniqueConstraint
from repository.tables.users import Base


def create_users_foreign_key(is_primary_key):
    """
    This function creates a column with user_id as a foregin key.
    """
    return Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        primary_key=is_primary_key,
    )


def create_content_foreign_key(is_primary_key):
    """
    This function creates a column with content_id as a foregin key.
    """
    return Column(
        Integer,
        ForeignKey("contents.content_id", ondelete="CASCADE"),
        nullable=False,
        primary_key=is_primary_key
    )


# pylint: disable=too-few-public-methods
# pylint: disable=too-many-instance-attributes
class Post(Base):
    """
    Class that represents the post class on the database.
    """

    __tablename__ = "posts"

    post_id = Column(Integer, primary_key=True)
    user_poster_id = create_users_foreign_key(False)
    user_creator_id = create_users_foreign_key(False)
    content_id = create_content_foreign_key(False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # pylint: disable=too-many-arguments
    def __init__(self, user_poster_id, user_creator_id, content_id):
        self.user_poster_id = user_poster_id
        self.user_creator_id = user_creator_id
        self.content_id = content_id


# pylint: disable=too-few-public-methods
# pylint: disable=too-many-instance-attributes
class Content(Base):
    """
    Class that represents the content class on the database.
    """

    __tablename__ = "contents"

    content_id = Column(Integer, primary_key=True)
    text = Column(String(1000), unique=False, nullable=True)  # 1K
    image = Column(String(1000), unique=False, nullable=True)  # 1K

    # pylint: disable=too-many-arguments
    def __init__(self, text, image):
        self.text = text
        self.image = image


# pylint: disable=too-few-public-methods
# pylint: disable=too-many-instance-attributes
class Like(Base):
    """
    Class that represents the like relation on the data base.
    """

    __tablename__ = "likes"

    content_id = create_content_foreign_key(True)
    user_id = create_users_foreign_key(True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    _table_args__ = (UniqueConstraint("user_id", "content_id"),)

    # pylint: disable=too-many-arguments
    def __init__(self, content_id, user_id):
        self.content_id = content_id
        self.user_id = user_id


# pylint: disable=too-few-public-methods
# pylint: disable=too-many-instance-attributes
class Hashtag(Base):
    """
    Class that represents the hashtag table on the db
    """

    __tablename__ = "hashtags"

    # We disable duplicate code here since it is a table and the
    # foreign key is the same in all tables
    # pylint: disable=R0801
    content_id = create_content_foreign_key(True)
    hashtag = Column(String(75), nullable=False, primary_key=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    _table_args__ = (UniqueConstraint("content_id", "hashtag"),)

    def __init__(self, content_id, hashtag):
        self.content_id = content_id
        self.hashtag = hashtag