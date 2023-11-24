"""
Queries for creating and deleting recent words for trending topics
"""
from typing import List
from sqlalchemy import Delete
from sqlalchemy.exc import IntegrityError
from collections import Counter

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.common_setup import *

# pylint: disable=C0114, W0401, W0614, E0401
from repository.errors import (
    DatabaseError,
)

# pylint: disable=C0114, W0401, W0614, E0401
from repository.tables.posts import RecentWord


# --------------------- AUXILIARY FUNCTIONS ---------------------

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string

nltk.download("stopwords")
nltk.download("punkt")

def get_keywords(text):
    words = word_tokenize(text)
    keywords = [
        word.lower()
        for word in words
        if word.isalnum()
        and word.lower() not in stopwords.words("english")
        and word.lower() not in stopwords.words("spanish")
        and word not in string.punctuation
    ]
    return keywords


# ----- CREATE ------


# pylint: disable=R0801
def create_recent_words(post_id: int, text: str):
    """
    Creates a recent words for a post
    """
    recent_words = get_keywords(text)
    try:
        for recent_word in recent_words:
            new_recent_word = RecentWord(post_id=post_id, recent_word=recent_word)

            # similar lines
            # pylint: disable=R0801
            session.add(new_recent_word)
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise DatabaseError from error


# ----- DELETE ------

# Por ahora solo para debug, esto se va a tener que hacer automaticamente
# pylint: disable=R0801
def delete_recent_words_for_content(post_id):
    """
    Deletes all hashtags from that particular post_id
    """
    try:
        delete_query = Delete(RecentWord).where(RecentWord.post_id == post_id)
        result = session.execute(delete_query)
        session.commit()
        return result.rowcount
    except IntegrityError as error:
        session.rollback()
        raise DatabaseError from error
    
# --------------------- GET ---------------------


def get_trending_topics(amount, offset):
    palabras_clave_frecuentes = (
        session.query(RecentWord.recent_word)
        .group_by(RecentWord.recent_word)
        .order_by(Counter(RecentWord.recent_word).desc())
        .limit(amount)
        .offset(offset)
        .all()
    )

    trending_topics = [palabra[0] for palabra in palabras_clave_frecuentes]
    return trending_topics

# TODO
def cleanup_trending_topics():
    return