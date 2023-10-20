"""
Queries for creating and deleting reposts
"""

from typing import List
from sqlalchemy import Delete
from sqlalchemy.exc import IntegrityError

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.common_setup import *

# pylint: disable=C0114, W0401, W0614, E0401
from repository.errors import (
    DatabaseError,
)

# pylint: disable=C0114, W0401, W0614, E0401
from repository.errors import (
    PostNotFound,
    DatabaseError,
    UserWithouPermission,
)

# pylint: disable=C0114, W0401, W0614, E0401
from repository.tables.posts import Post, Content

# ----- CREATE ------


def create_repost(post_id: int, user_reposter_id: int):
    """
    Create a repost of a post
    """
    try:
        post_and_content = (session.query(Content)
                            .join(Post, Post.content_id == Content.content_id)
                            .filter(Post.post_id == post_id)
                            .first())
        
        #original post to repost not found
        if post_and_content is None:
            raise PostNotFound()
        
        #user wants to repost a post --> not allowed
        if post_and_content.user_creator_id != post_and_content.user_poster_id:
            raise UserWithouPermission()
        
        #user wants to repost from a private account --> not allowed
        if not user_is_public(post_and_content.user_creator_id):
            raise UserWithouPermission()
        
        post = Post(
            user_poster_id = user_reposter_id,
            user_creator_id = post_and_content.user_creator_id,
            content_id = post_and_content.content_id,
        )

        return
    except IntegrityError as error:
        session.rollback()
        raise DatabaseError from error


# ----- DELETE ------

def delete_repost(post_id):
    """
    Deletes the repost with that id, if found
    """
    try:
        repost = session.query(Post).filter(Post.id == post_id).first()
        if repost is None:
            raise PostNotFound()
        
        session.delete(repost)
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise DatabaseError from error


def delete_reposts_for_content(content_id):
    """
    Deletes all reposts from that content_id
    """
    try: 
        delete_reposts_query = Delete(Post).where(Post.content_id == content_id)
        session.execute(delete_reposts_query)
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise DatabaseError from error



   