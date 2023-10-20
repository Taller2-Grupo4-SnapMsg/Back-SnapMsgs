"""
Queries for creating and deleting hashtags
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


def create_hashtags(content_id: int, hashtags: List[str]):
    """
    Creates a hashtag for a post
    """
    try:
        for hashtag in hashtags:
            new_hashtag = Hashtag(content_id=content_id, hashtag=hashtag)
            session.add(new_hashtag)
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise DatabaseError from error


# ----- DELETE ------


def delete_hashtags_for_content(content_id):
    """
    Deletes all hashtags from that particular content_id
    """
    try:
        delete_query = Delete(Hashtag).where(Hashtag.content_id == content_id)
        result = session.execute(delete_query)
        session.commit()
        return result.rowcount
    except IntegrityError as error:
        session.rollback()
        raise DatabaseError from error
