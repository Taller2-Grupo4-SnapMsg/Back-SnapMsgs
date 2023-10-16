"""
Archivo con algunas pruebas de la base de datos
"""
from sqlalchemy.exc import IntegrityError

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.common_setup import *

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.queries_hashtag import *

# pylint: disable=C0114, W0401, W0614, E0401
from repository.errors import (
    PostNotFound,
    UserNotFound,
    DatabaseError,
    UserWithouPermission,
)

# pylint: disable=C0114, W0401, W0614, E0401
from repository.tables.posts import Post


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


def update_post(post_id, user_id, content, image, hashtags):
    """
    Updates posts contents, image and hashtags
    """
    try:
        post = (
        session.query(Post).filter(Post.id == post_id, Post.user_id == user_id).first()
        )

        if post is None:
            raise PostNotFound()

        if post.user_id != user_id:
            raise UserWithouPermission()
        post.content = content
        post.image = image
        delete_hashtags_for_post(id_post)
        create_hashtags(id_post, hashtags)
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise DatabaseError from error
    return post



def delete_post(id_post, user_id):
    """
    Deletes the folowing relation between the two users.
    """

    post = session.query(Post).filter(Post.id == id_post).first()
    if post is None:
        raise PostNotFound()
    if post.user_id != user_id:
        raise UserWithouPermission()
    if post:
        delete_hashtags_for_post(id_post)
        session.delete(post)
        session.commit()
        return
    raise UserNotFound()
