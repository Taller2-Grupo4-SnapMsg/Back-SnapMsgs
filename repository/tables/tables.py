# tables.py

"""
This module represents the tables on the database of the users' microservice 
"""

import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, UniqueConstraint
from sqlalchemy.orm import declarative_base

LocalBase = declarative_base()


# pylint: disable=too-few-public-methods
# pylint: disable=too-many-instance-attributes
class Posts(LocalBase):
    """
    Class that represents the user class on the database.
    """

    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)

    posted_at = Column(DateTime, default=datetime.datetime.utcnow)
    # verificar si 800 caracteres es mucho para un tweet
    content = Column(String(800), unique=False, nullable=True)
    # verificar que image y content no sean NULL a la vez
    image = Column(String(100), unique=False, nullable=True)

    # pylint: disable=too-many-arguments
    def __init__(self, user_id, content, image):
        self.user_id = user_id
        self.content = content
        self.image = image


# id_post = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
# user_id = Column(Integer, nullable=False)
# created_at = Column(DateTime, default=datetime.datetime.utcnow)
# _table_args__ = (
#     PrimaryKeyConstraint('id_post', 'user_id'),
# )


class Likes(LocalBase):
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
    user_id = Column(Integer, nullable=False, primary_key=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    _table_args__ = (UniqueConstraint("user_id", "id_post"),)

    # pylint: disable=too-many-arguments
    def __init__(self, id_post, user_id):
        self.id_post = id_post
        self.user_id = user_id
