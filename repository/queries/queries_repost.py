# pylint: disable=R0801
"""
Archivo con algunas pruebas de la base de datos
"""
from sqlalchemy.exc import IntegrityError

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.common_setup import *

# pylint: disable=C0114, W0401, W0614, E0401
from repository.errors import (
    RepostNotFound,
    DatabaseError,
)

# pylint: disable=C0114, W0401, W0614, E0401
from repository.tables.posts import Repost


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
