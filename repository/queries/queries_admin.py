"""
Queries for getting posts, reposts, and all their info
"""
from sqlalchemy.orm import aliased
from sqlalchemy import and_

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.common_setup import *

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.queries_global import *

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.subqueries_get import *

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.queries_get import *

# pylint: disable=C0114, W0401, W0614, E0401
from repository.tables.posts import *

# pylint: disable=C0114, W0401, W0614, E0401
from repository.tables.users import *

from repository.errors import DatabaseError

# pylint: disable=R0801
# I disable the "Similar lines in 2 files" because I don't want to stick an
# if in two functions that do not do the same.


def get_posts_and_reposts_for_admin_subquery():
    """
    Returns query that gets all posts and reposts (with their respective info)
    and if this user liked or reposted the post
    """
    subquery_likes_count = create_subquery_likes_count()
    how_many_likes = create_how_many_likes(subquery_likes_count)

    subquery_repost_count = create_subquery_resposts_count()
    how_many_reposts = create_how_many_reposts(subquery_repost_count)

    hashtags_subquery = create_subquery_hashtags()
    mentions_subquery = create_subquery_mentions()

    # pylint: disable=C0103
    # "Variable name "User2" doesn't conform to snake_case naming style"
    User2 = aliased(User)
    query = (
        session.query(
            Post,
            Content,
            User,
            User2,
            hashtags_subquery.c.hashtags,
            mentions_subquery.c.mentions,
            how_many_likes,
            how_many_reposts,
        )
        .join(Content, Post.content_id == Content.content_id)
        .join(User, User.id == Post.user_poster_id)
        .join(User2, User2.id == Post.user_creator_id)
        .join(
            subquery_likes_count,
            Post.content_id == subquery_likes_count.c.content_id,
            isouter=True,
        )
        .join(
            subquery_repost_count,
            Post.content_id == subquery_repost_count.c.content_id,
            isouter=True,
        )
        .join(
            hashtags_subquery,
            Post.content_id == hashtags_subquery.c.content_id,
            isouter=True,
        )
        .join(
            mentions_subquery,
            Post.content_id == mentions_subquery.c.content_id,
            isouter=True,
        )
    )
    return query


def get_posts_and_reposts_for_admin_user_id(user_id, start, ammount):
    """
    Get all the posts and reposts for the admin
    """
    try:
        posts = get_posts_and_reposts(user_id).filter(
            and_(User.id == user_id, Post.user_creator_id == user_id)
        )
        return posts.order_by(Post.created_at.desc()).offset(start).limit(ammount).all()
    except IntegrityError as error:
        session.rollback()
        raise DatabaseError from error


def get_posts_and_reposts_for_admin(start, ammount):
    """,
    Get all the posts and reposts for the admin
    """
    try:
        posts = get_posts_and_reposts_for_admin_subquery()
        return posts.order_by(Post.created_at.desc()).offset(start).limit(ammount).all()
    except IntegrityError as error:
        session.rollback()
        raise DatabaseError from error
