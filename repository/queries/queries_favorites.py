"""
Queries for creating and deleting favorites
"""
from sqlalchemy import Delete, or_
from sqlalchemy.exc import IntegrityError

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.common_setup import *
from repository.queries.queries_global import execute_delete_query
from repository.queries.queries_get import get_posts_and_reposts
from repository.queries.queries_get import is_public

from repository.errors import (
    DatabaseError,
    FavoriteNotFound,
    PostNotFound,
)

# pylint: disable=C0114, W0401, W0614, E0401
from repository.tables.posts import Favorite, Post
from repository.tables.users import Following

# ----- CREATE ------


###QUEDA PROBAR
def create_favorite(post_id: int, content_id: int, user_id: int):
    """
    Creates a favorite from post
    """
    try:
        post = session.query(Post).filter(Post.post_id == post_id).first()
        if post is None:
            raise PostNotFound()

        favorite = Favorite(content_id, user_id)
        session.add(favorite)
        # pylint: disable=R0801
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise DatabaseError from error


# ----- DELETE ------


###QUEDA PROBAR
def delete_favorite(content_id: int, user_id: int):
    """
    Deletes all favorites from that particular content_id
    """
    try:
        favorite = (
            session.query(Favorite)
            .filter(Favorite.content_id == content_id, Favorite.user_id == user_id)
            .first()
        )

        if favorite is None:
            raise FavoriteNotFound()

        session.delete(favorite)
        # pylint: disable=R0801
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise DatabaseError from error


###QUEDA PROBAR
def delete_favorites_for_content(content_id):
    """
    Deletes all hashtags from that particular content_id
    """
    delete_favorites_query = Delete(Favorite).where(Favorite.content_id == content_id)
    execute_delete_query(delete_favorites_query)


###QUEDA PROBAR
def get_favorites_from_user(user_visitor_id, user_visited_id, oldest_date, amount):
    """
    Get posts and reposts, with all their info, where the first
    id is the user that is
    """
    query_posts = get_posts_and_reposts(user_visitor_id)

    query_final = (
        query_posts.filter(Favorite.user_id == user_visited_id)
        .filter(
            or_(
                user_visited_id == user_visitor_id,
                Post.user_poster_id.in_(
                    session.query(Following.following_id).filter(
                        Following.user_id == user_visitor_id
                    )
                ),
                bool(is_public(user_visited_id)),
            )
        )
        .order_by(Post.created_at.desc())
        .filter(Post.created_at < oldest_date)
    )

    return query_final.limit(amount)
