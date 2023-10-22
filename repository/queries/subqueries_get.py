"""
Queries for getting posts, reposts, and all their info
"""

from sqlalchemy import case, func
from sqlalchemy.dialects.postgresql import array_agg

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.common_setup import *

# pylint: disable=C0114, W0401, W0614, E0401
from repository.tables.posts import *

# pylint: disable=C0114, W0401, W0614, E0401
from repository.tables.users import *


def create_subquery_likes_count():
    """
    Create subquery that counts the amount of likes each content has
    """
    return (
        # func.count is not callable, when it actually is
        # pylint: disable=E1102
        session.query(Like.content_id, func.count(1).label("like_count"))
        .group_by(Like.content_id)
        .subquery()
    )


def create_subquery_resposts_count():
    """
    Create subquery that counts the amount of reposts each content has
    """
    return (
        # func.count is not callable, when it actually is
        # pylint: disable=E1102
        session.query(Post.content_id, func.count(1).label("repost_count"))
        .group_by(Post.content_id)
        .subquery()
    )


def create_subquery_my_like_count_by_user(user_id):
    """
    To check if the user liked the content or not
    The column will have a 1 if the user did like, or a 0 if they didnt
    """
    return (
        # func.count is not callable, when it actually is
        # pylint: disable=E1102
        session.query(Like.content_id, func.count(1).label("user_like_count"))
        .filter(Like.user_id == user_id)
        .group_by(Like.content_id)
        .subquery()
    )


def create_subquery_my_reposts_count(user_visitor_id):
    """
    To check if the user reposted the content or not
    The column will have a 1 if the user did repost, or a 0 if they didnt
    """
    return (
        # func.count is not callable, when it actually is
        # pylint: disable=E1102
        session.query(Post.content_id, func.count(1).label("user_repost_count"))
        .filter(
            Post.user_poster_id == user_visitor_id,
            Post.user_creator_id != user_visitor_id,
        )
        .group_by(Post.content_id)
        .subquery()
    )


def create_subquery_hashtags():
    """
    Create a subquery that retrieves hashtags per 'content_id'.
    """
    return (
        session.query(Hashtag.content_id, array_agg(Hashtag.hashtag).label("hashtags"))
        .group_by(Hashtag.content_id)
        .subquery()
    )


def create_did_i_like_column(subquery_user_like_count):
    """
    Create a subquery that checks if the value in the user_like_count
    column is 0 (--> the user didnt like the content) or 1
    (--> the user did like the content), and replaces each value with
    a False or True respetively
    """
    return case(
        (subquery_user_like_count.c.user_like_count != 0, True), else_=False
    ).label("did_I_like")


def create_did_i_repost_column(subquery_user_repost_count):
    """
    Create a subquery that checks if the value in the user_repost_count
    column is 0 (--> the user didnt repost the content) or 1
    (--> the user did repost the content), and replaces each value with
    a False or True respetively
    """
    return case(
        (subquery_user_repost_count.c.user_repost_count != 0, True), else_=False
    ).label("did_I_repost")


def create_how_many_reposts(subquery_repost_count):
    """
    Creates a subquery that counts the amount of reposts each content has.
    The -1 is to not count the original post as a repost
    """
    return (subquery_repost_count.c.repost_count - 1).label("how_many_reposts")


def create_how_many_likes(subquery_likes_count):
    """
    Creates a subquery that counts the amount of likes each content has.
    """
    return subquery_likes_count.c.like_count.label("how_many_likes")


def create_subquery_hashtags_interests(user_id):
    """
    Create subquery that returns all the content_id that have at least one
    hashtag that correspons to at least one interest that the user_id has
    """
    return (
        session.query(Hashtag.content_id)
        .filter(Hashtag.hashtag == Interests.interest)
        .filter(Interests.user_id == user_id)
        .distinct()
        .subquery()
    )


def create_subquery_posts_from_followd(user_id):
    """
    Create subquery that returns all the posts from users that the user_id follows
    """
    return (
        session.query(Post.post_id)
        .join(Following, Following.following_id == Post.user_poster_id)
        .filter(Following.user_id == user_id)
        .distinct()
        .subquery()
    )
