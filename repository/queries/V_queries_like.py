# pylint: disable=R0801
"""
Archivo con algunas pruebas de la base de datos
"""
from sqlalchemy.exc import IntegrityError

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.common_setup import *

# pylint: disable=C0114, W0401, W0614, E0401
from repository.errors import (
    PostNotFound,
    LikeNotFound,
    DatabaseError,
)

# pylint: disable=C0114, W0401, W0614, E0401
from repository.tables.posts import Post, Like

# ----------- Post --------------


def create_like(id_post, user_id):
    """
    Create a like
    """
    try:
        like = Like(id_post, user_id)
        session.add(like)
        session.commit()
        return like
    except IntegrityError as error:
        session.rollback()
        raise DatabaseError from error


# ----------- Get --------------


def get_the_number_of_likes(post_id):
    """
    Returns the number of likes.
    """
    post = session.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise PostNotFound()
    return session.query(Like).filter(Like.id_post == post_id).count()


# ----------- Delete --------------


def delete_like(user_id, post_id):
    """
    Deletes the folowing relation between the two users.
    """
    like = (
        session.query(Like)
        .filter(Like.user_id == user_id, Like.id_post == post_id)
        .first()
    )
    if like:
        session.delete(like)
        session.commit()
        return
    raise LikeNotFound()

def delete_likes_for_post(post_id):
    """
    Elimina todos los hashtags de una publicación específica.
    """
    delete_query = Delete(Like).where(Like.id_post == post_id)
    result = session.execute(delete_query)
    session.commit()
    return result.rowcount
