"""
Archivo con algunas pruebas de la base de datos
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
from repository.tables.posts import Hashtag

# ----- CREATE ------


def create_hashtags(id_post: int, hashtags: List[str]):
    print(hashtags)
    try:
        for hashtag in hashtags:
            new_hashtag = Hashtag(id_post=id_post, hashtag=hashtag)
            session.add(new_hashtag)
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise DatabaseError from error
    return


# ----- DELETE ------


def delete_hashtags_for_post(post_id):
    """
    Elimina todos los hashtags de una publicación específica.
    """
    delete_query = Delete(Hashtag).where(Hashtag.id_post == post_id)
    result = session.execute(delete_query)
    session.commit()
    return result.rowcount
