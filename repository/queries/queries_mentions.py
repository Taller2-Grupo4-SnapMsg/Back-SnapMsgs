"""
Queries for creating and deleting mentions
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
from repository.tables.posts import Mention
from repository.tables.users import User

# ----- CREATE ------


# pylint: disable=R0801
def create_mentions(content_id: int, usernames: List[str]):
    """
    Creates a mention for a post
    """
    try:
        for username in usernames:
            user = session.query(User).filter_by(username=username).first()
            # si no existe el usuario, no se crea la mencion, se deberia lanzar excepcion?
            if user:
                new_mention = Mention(content_id=content_id, user_mention_id=user.id)
                # similar lines
                # pylint: disable=R0801
                session.add(new_mention)
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise DatabaseError from error


# ----- DELETE ------


# pylint: disable=R0801
def delete_mentions_for_content(content_id):
    """
    Deletes all mentions from that particular content_id
    """
    try:
        delete_query = Delete(Mention).where(Mention.content_id == content_id)
        result = session.execute(delete_query)
        session.commit()
        return result.rowcount
    except IntegrityError as error:
        session.rollback()
        raise DatabaseError from error
