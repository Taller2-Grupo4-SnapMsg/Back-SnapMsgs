# tables.py

"""
This module represents the tables on the database of the users' microservice 
"""

import datetime
from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint
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
    content = Column(
        String(800), unique=False, nullable=True
    )  # verificar si 800 caracteres es mucho para un tweet
    image = Column(
        String(100), unique=False, nullable=True
    )  # verificar que image y content no sean NULL a la vez

    # pylint: disable=too-many-arguments
    def __init__(self, user_id, posted_at, content, image):
        self.user_id = user_id
        self.posted_at = posted_at
        self.content = content
        self.image = image


class Likes(LocalBase):
    """
    Class that represents the following relation on the data base.
    """

    __tablename__ = "likes"

    # Obtain metadata from repo_users
    # engine_users = create_engine(os.environ.get("DB_USERS_URI"))
    # metadata_repo_users = MetaData(bind=engine_users)
    # metadata_repo_users.reflect()

    id = Column(
        Integer,
        nullable=False,
        primary_key=True,
    )

    id_post = Column(
        Integer,
        nullable=False,
        primary_key=True,
    )

    user_id = Column(Integer, nullable=False)

    _table_args__ = (
        UniqueConstraint("user_id", "id_post"),
    )  # a user can't like a post twice

    # pylint: disable=too-many-arguments
    def __init__(self, id_post, user_id):
        self.id_post = id_post
        self.user_id = user_id
