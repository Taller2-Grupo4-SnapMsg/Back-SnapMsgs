"""
This file contains the queries for the trending topics
"""
from datetime import datetime, timedelta
from sqlalchemy import func, desc

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.common_setup import *
from repository.queries.queries_get import get_posts_and_reposts
from repository.tables.posts import Hashtag, Post
from repository.tables.users import User


def get_trending_topics_with_count(offset, amount, days):
    """
    Returns the trending topics of the last x days
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    trending_topics = (
        # pylint: disable=E1102
        session.query(Hashtag.hashtag, func.count(Post.post_id).label("post_count"))
        .join(Post, Hashtag.content_id == Post.content_id)
        .filter(Hashtag.created_at >= start_date, Hashtag.created_at <= end_date)
        .group_by(Hashtag.hashtag)
        .order_by(desc("post_count"))
    )

    return trending_topics.offset(offset).limit(amount)


def get_posts_on_a_trending_topic(user_id, hashtag, offset, amount):
    """
    Returns the posts of a trending topic
    """
    query_posts = get_posts_and_reposts(user_id)

    query_final = (
        query_posts.join(Hashtag, Post.content_id == Hashtag.content_id)
        .filter(Hashtag.hashtag == hashtag)
        # pylint: disable=C0121
        .filter(User.is_public == True)
        .order_by(desc(Post.created_at))
    )

    return query_final.offset(offset).limit(amount)
