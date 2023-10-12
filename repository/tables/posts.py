# tables.py

"""
This module represents the tables on the database of the users' microservice 
"""

import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, UniqueConstraint
from repository.tables.users import Base
from repository.tables.users import create_users_foreign_key


# pylint: disable=too-few-public-methods
# pylint: disable=too-many-instance-attributes
class Post(Base):
    """
    Class that represents the user class on the database.
    """

    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    posted_at = Column(DateTime, default=datetime.datetime.utcnow)
    content = Column(String(1000), unique=False, nullable=True)  # 1K
    image = Column(String(1000), unique=False, nullable=True)  # 1K

    # pylint: disable=too-many-arguments
    def __init__(self, user_id, content, image):
        self.user_id = user_id
        self.content = content
        self.image = image


class Like(Base):
    """
    Class that represents the following relation on the data base.
    """

    __tablename__ = "likes"

    id_post = Column(
        Integer,
        ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
    )

    user_id = create_users_foreign_key()

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    _table_args__ = (UniqueConstraint("user_id", "id_post"),)

    # pylint: disable=too-many-arguments
    def __init__(self, id_post, user_id):
        self.id_post = id_post
        self.user_id = user_id


class Repost(Base):
    """
    Class that represents the retweets relation in the database.
    """

    __tablename__ = "reposts"

    id_post = Column(
        Integer,
        ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
    )
    user_id = create_users_foreign_key()

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    _table_args__ = (UniqueConstraint("user_id", "id_post"),)

    # pylint: disable=too-many-arguments
    def __init__(self, id_post, user_id):
        self.id_post = id_post
        self.user_id = user_id


class Hashtag(Base):
    """
    Class that represents the interests table of users
    """

    __tablename__ = "hashtags"

    # We disable duplicate code here since it is a table and the
    # foreign key is the same in all tables
    # pylint: disable=R0801
    id_post = Column(
        Integer,
        ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
    )

    hashtag = Column(String(75), nullable=False, primary_key=True)

    _table_args__ = (UniqueConstraint("id_post", "hashtag"),)

    def __init__(self, id_post, hashtag):
        self.id_post = id_post
        self.hashtag = hashtag