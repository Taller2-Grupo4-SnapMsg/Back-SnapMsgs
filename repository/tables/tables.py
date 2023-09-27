# tables.py

"""
This module represents the tables on the database of the users' microservice 
"""

import datetime
from sqlalchemy import Column, Integer, Table
from sqlalchemy import String, DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship

import os
from sqlalchemy import create_engine
from sqlalchemy import MetaData

Base = declarative_base()


# pylint: disable=too-few-public-methods
# pylint: disable=too-many-instance-attributes
class Posts(Base):
    """
    Class that represents the user class on the database.
    """
    
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    email_user = Column(String(100), 
        ForeignKey("users.emails", ondelete="CASCADE"),
        unique=True, 
        nullable=False)
    posted_at = Column(DateTime, default=datetime.datetime.utcnow)
    content = Column(String(800), unique=False, nullable=True) #verificar si 800 caracteres es mucho para un tweet
    image = Column(String(100), unique=False, nullable=True) #verificar que image y content no sean NULL a la vez
    
    # pylint: disable=too-many-arguments
    def __init__(
        self,
        email_user,
        posted_at,
        content,
        image
    ):
        self.email_user = email_user
        self.posted_at = posted_at
        self.content = content
        self.image = image

# Create the engine for the 'users' database
engine_users = create_engine(os.environ.get("DB_USERS_URI"))

# Crea una instancia de MetaData
metadata_users = MetaData()

# Enlaza la MetaData al motor de la base de datos después de crearla
metadata_users.bind = engine_users

class Likes(Base):
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
        ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
    )
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Establish the relationship to the users table in the other database
    #user = relationship('User', back_populates='likes', foreign_keys=[user_id], bind=engine_users)
    users = Table('users', metadata_users, autoload=True)

    _table_args__ = (UniqueConstraint("user_id", "id_post"),)  # a user can't like a post twice

    # pylint: disable=too-many-arguments
    def __init__(self, id_post, user_id):
        self.id_post = id_post
        self.user_id = user_id
