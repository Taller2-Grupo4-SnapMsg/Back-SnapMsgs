"""
Global queries and functions that could be reused in other queries
"""

"""
Archivo con algunas pruebas de la base de datos
"""
from sqlalchemy import and_, literal_column, or_, desc
from sqlalchemy import func
from sqlalchemy.orm import aliased

from repository.errors import PostNotFound

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.common_setup import *

# pylint: disable=C0114, W0401, W0614, E0401
from repository.tables.posts import Post, Like, Hashtag

# pylint: disable=C0114, W0401, W0614, E0401
from repository.tables.users import User, Following, Interests


def is_following(user_id, user_id_to_check_if_following):
    """
    Returns True if the user with the given id is following
    the user with the given id.
    """
    following = (
        session.query(Following)
        .filter(Following.user_id == user_id)
        .filter(Following.following_id == user_id_to_check_if_following)
        .first()
    )
    return following is not None

def get_content_id_from_post(post_id):
    """
    Returns True if the user with the given id is following
    the user with the given id.
    """
    post = (
        session.query(Post)
        .filter(Post.post_id == post_id)
        .first()
    )
    if post is None:
        raise PostNotFound()
    return post.content_id


def is_public(user_id):
    """
    Returns True if the user is public.
    """
    public = (
        session.query(User)
        .filter(User.id == user_id)
        # pylint: disable=C0121
        .filter(User.is_public == True)
        .first()
    )
    return public is not None
