"""
Queries for creating and deleting likes
"""
from sqlalchemy import Delete
from sqlalchemy.exc import IntegrityError

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.common_setup import *
from repository.queries.queries_global import execute_delete_query

# pylint: disable=C0114, W0401, W0614, E0401
from repository.errors import (
    DatabaseError,
    LikeNotFound,
    PostNotFound,
    CannotLikeRepost,
)

# pylint: disable=C0114, W0401, W0614, E0401
from repository.tables.posts import Like, Post

# ----- CREATE ------


def create_like(post_id: int, content_id: int, user_id: int):
    """
    Creates a hashtag for a post
    """
    try:
        post = session.query(Post).filter(Post.post_id == post_id).first()
        if post is None:
            raise PostNotFound()

        if post.user_creator_id != post.user_poster_id:
            raise CannotLikeRepost()

        like = Like(content_id, user_id)
        session.add(like)
        # pylint: disable=R0801
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise DatabaseError from error


# ----- DELETE ------


def delete_like(content_id: int, user_id: int):
    """
    Deletes all hashtags from that particular content_id
    """
    try:
        like = (
            session.query(Like)
            .filter(Like.content_id == content_id, Like.user_id == user_id)
            .first()
        )
        if like is None:
            raise LikeNotFound()

        session.delete(like)
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise DatabaseError from error


def delete_likes_for_content(content_id):
    """
    Deletes all hashtags from that particular content_id
    """
    delete_likes_query = Delete(Like).where(Like.content_id == content_id)
    execute_delete_query(delete_likes_query)
