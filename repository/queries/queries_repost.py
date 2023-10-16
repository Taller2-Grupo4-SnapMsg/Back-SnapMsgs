# pylint: disable=R0801
"""
Archivo con algunas pruebas de la base de datos
"""
from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.common_setup import *

# pylint: disable=C0114, W0401, W0614, E0401
from repository.errors import (
    PostNotFound,
    RepostNotFound,
    UserNotFound,
    DatabaseError,
)

# pylint: disable=C0114, W0401, W0614, E0401
from repository.tables.posts import Post, Repost

# pylint: disable=C0114, W0401, W0614, E0401
from repository.tables.users import User


# ----------- Post --------------


def create_repost(id_post, user_id):
    """
    Create a repost
    """
    try:
        repost = Repost(id_post, user_id)
        session.add(repost)
        session.commit()
        return repost
    except IntegrityError as error:
        session.rollback()
        raise DatabaseError from error


# ----------- Get --------------


def get_reposts_from_post(post_id):
    """
    Retrieve all the reposts for a specific post.

    If the post does not exist, raises a PostNotFound exception.
    """
    post = session.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise PostNotFound()

    users = (
        session.query(User)
        .join(Repost, User.id == Repost.user_id)
        .filter(Repost.id_post == post_id)
        .all()
    )

    return users


def get_the_number_of_reposts_of_a_post(post_id):
    """
    Returns the number of repost.
    """
    post = session.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise PostNotFound()
    return session.query(Repost).filter(Repost.id_post == post_id).count()


def get_the_posts_reposted_by_the_user(user_id):
    """
    Retrieves posts reposted by a specific user, with information
    about the post and the user who made the post.
    """
    user = session.query(User).filter(User.id == user_id).first()

    if not user:
        raise UserNotFound()

    reposted_posts = (
        session.query(Post, User)
        .join(Repost, Post.id == Repost.id_post)
        .join(User, Post.user_id == User.id)
        .filter(Repost.user_id == user_id)
        .order_by(desc(Post.posted_at))
        .all()
    )

    return reposted_posts


def get_all_the_reposts():
    """
    Retrieve all reposts in the system.
    """
    return session.query(Repost).all()


# ----------- Delete --------------


def delete_repost(user_id, post_id):
    """
    Delete repost of a post
    """
    repost = (
        session.query(Repost)
        .filter(Repost.user_id == user_id, Repost.id_post == post_id)
        .first()
    )
    if repost:
        session.delete(repost)
        session.commit()
        return
    raise RepostNotFound()


def delete_reposts():
    """
    Deletes all reposts.
    """
    session.query(Repost).delete()
    session.commit()
