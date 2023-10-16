"""
Archivo con algunas pruebas de la base de datos
"""
from typing import List
from sqlalchemy import and_, exists, or_, func
from sqlalchemy import desc
from sqlalchemy.orm import aliased
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.common_setup import *

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.queries_hashtag import *

# pylint: disable=C0114, W0401, W0614, E0401
from repository.errors import (
    PostNotFound,
    UserNotFound,
    NegativeOrZeroAmount,
    DatabaseError,
)

# pylint: disable=C0114, W0401, W0614, E0401
from repository.tables.posts import Post, Like, Repost

# pylint: disable=C0114, W0401, W0614, E0401
from repository.tables.users import User, Following


def create_post(user_id, content, image):
    """
    Create a post made by the user_id, with that content and image
    """
    post = Post(
        user_id=user_id,
        content=content,
        image=image,
    )

    try:
        session.add(post)
        session.commit()
        return post
    except IntegrityError as error:
        session.rollback()
        raise DatabaseError from error


# ------------- GET ----------------


def update_post(post_id, user_id, content, image):
    post = (
        session.query(Post).filter(Post.id == post_id, Post.user_id == user_id).first()
    )

    if post is None:
        raise PostNotFound()

    post.content = content
    post.image = image
    session.commit()
    return post


def delete_post(id_post):
    """
    Deletes the folowing relation between the two users.
    """
    delete_hashtags_for_post(id_post)
    post = session.query(Post).filter(Post.id == id_post).first()
    if post:
        session.delete(post)
        session.commit()
        return
    raise UserNotFound()


# ----------------No se usan, quedan por los tests ----------------


# listo
def get_posts_by_user_id(user_id):
    """
    Searches all posts from that user

    The return value is a list of Posts.
    The posts are ordered from newest to oldest
    """
    posts = (
        session.query(Post, User)
        .join(Post)
        .filter(Post.user_id == user_id)
        .order_by(Post.posted_at.desc())
    )
    if not posts:
        raise UserNotFound
    return posts


def get_posts_by_user_and_date(user_id, date):
    """
    Searches for posts made by the user on the specific date

    The return value is a list of Posts
    The posts are ordered from newest to oldest
    """
    return (
        session.query(Post)
        .filter(and_(Post.user_id == user_id, Post.posted_at == date))
        .order_by(desc(Post.posted_at))
        .all()
    )


def get_posts_by_user_between_dates(user_id, start_date, end_date):
    """
    Searches the posts made by the user on a specific time frame

    The return value is a list of Posts.
    The posts are ordered from newest to oldest
    """
    return (
        session.query(Post)
        .filter(
            and_(Post.user_id == user_id, Post.posted_at.between(start_date, end_date))
        )
        .order_by(desc(Post.posted_at))
        .all()
    )


# listo
def get_newest_post_by_user(user_id):
    """
    Searches the newest post made by that user

    The return value is a Post.
    """
    post = (
        session.query(Post)
        .filter(Post.user_id == user_id)
        .order_by(desc(Post.posted_at))
        .first()
    )
    if not post:
        raise PostNotFound
    return post


# listo
def get_x_newest_posts_by_user(user_id, amount):
    """
    Searches the x amount of newest posts made by that user

    The return value is a list of Post.
    """
    if amount <= 0:
        raise NegativeOrZeroAmount

    posts = (
        session.query(Post)
        .filter(Post.user_id == user_id)
        .order_by(desc(Post.posted_at))
        .limit(amount)
        .all()
    )
    if not posts:
        raise UserNotFound
    return posts


def get_x_newest_posts(amount):
    """
    Retrieves all posts in db with all the corresponding user info.

    Raises:
        PostNotFound: If a post is not found.
    """

    if amount <= 0:
        raise NegativeOrZeroAmount

    results = (
        session.query(Post, User)
        .join(User, Post.user_id == User.id)
        .order_by(desc(Post.posted_at))
        .limit(amount)
        .all()
    )

    if not results:
        raise PostNotFound()

    return results


def put_post(modified_post):
    """
    Searches the post with the same id and updates it
    The function updates all the info from the post in the db
    with the info in the modified_post.
    Be sure everything that is allowed to be modified
    is in the modified_post!
    That is content, image and etiquetas

    Raises PostNotFound if not foun
    """
    existing_post = session.query(Post).filter(Post.id == modified_post.id).first()
    if not existing_post:
        raise PostNotFound

    # Update what we allow to be updated
    existing_post.content = modified_post.content
    existing_post.image = modified_post.image
    # falta modificar las etiquetas de las publicaciones

    session.commit()


def delete_posts_by_user(user_id):
    """
    Deletes the posts made by that user
    """
    post = session.query(Post).filter(Post.user_id == user_id).all()
    if post:
        session.delete(post)
        session.commit()
        return
    raise UserNotFound()


def delete_posts():
    """
    Deletes all posts.
    """
    session.query(Post).delete()
    session.commit()


def get_posts():
    """
    Retrieves all posts in db with all the corresponding user info.



    Raises:
        PostNotFound: If a post is not found.
    """

    results = (
        session.query(Post, User)
        .join(User, Post.user_id == User.id)
        .order_by(desc(Post.posted_at))
        .all()
    )

    if not results:
        raise PostNotFound()

    return results


def get_post_by_id(post_id):
    """
    Searches the specific post based on id

    The return value is a Post.
    """
    post = session.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise PostNotFound
    return post
