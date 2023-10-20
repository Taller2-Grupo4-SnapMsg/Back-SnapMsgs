"""
Queries for creating and deleting reposts
"""
from sqlalchemy import Delete
from sqlalchemy.exc import IntegrityError

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.common_setup import *

from repository.queries.queries_global import is_public

# pylint: disable=C0114, W0401, W0614, E0401
from repository.errors import (
    DatabaseError,
)

# pylint: disable=C0114, W0401, W0614, E0401
from repository.errors import (
    PostNotFound,
    DatabaseError,
    UserWithouPermission,
    RepostAlreadyMade
)

# pylint: disable=C0114, W0401, W0614, E0401
from repository.tables.posts import Post, Content

# ----- CREATE ------


def create_repost(post_id: int, user_reposter_id: int):
    """
    Create a repost of a post
    """
    try:
        post = (session.query(Post)
                            .filter(Post.post_id == post_id)
                            .first())
        
        #original post to repost not found
        if post is None:
            raise PostNotFound()
        
        #user wants to repost a post --> not allowed
        if post.user_creator_id != post.user_poster_id:
            raise UserWithouPermission()
        
        #user wants to repost from a private account --> not allowed
        if not is_public(post.user_creator_id):
            raise UserWithouPermission()

        repost_check = (session.query(Post)
                            .filter(Post.user_poster_id == user_reposter_id)
                            .filter(Post.user_creator_id == post.user_creator_id)
                            .filter(Post.content_id == post.content_id)
                            .first())
        
        #user wants to repost the same post twice
        if repost_check is not None:
            raise RepostAlreadyMade()
        
        repost = Post(
            user_poster_id = user_reposter_id,
            user_creator_id = post.user_creator_id,
            content_id = post.content_id,
        )

        session.add(repost)
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise DatabaseError from error


# ----- DELETE ------

def delete_repost(post_id, user_id):
    """
    Deletes the repost with that id, if found
    """
    try:
        repost = session.query(Post).filter(Post.post_id == post_id).first()
        if repost is None:
            raise PostNotFound()
        
        #trying to delete a post that was not made by this user
        if repost.user_poster_id != user_id: 
            raise UserWithouPermission()
        
        #trying to delete a post --> wrong endpoint
        if repost.user_creator_id == user_id: 
            raise UserWithouPermission()
        
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



   