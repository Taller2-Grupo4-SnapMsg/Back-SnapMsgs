"""
Queries for getting posts, reposts, and all their info
"""

from sqlalchemy import case, func

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.common_setup import *
# pylint: disable=C0114, W0401, W0614, E0401
from repository.tables.posts import *
# pylint: disable=C0114, W0401, W0614, E0401
from repository.tables.users import *


def create_subquery_likes_count():
    return session.query(Like.content_id, func.count().label('like_count')
                        ).group_by(Like.content_id
                        ).subquery()

def create_subquery_resposts_count():
    return session.query(Post.content_id, func.count().label('repost_count')
                        ).group_by(Post.content_id
                        ).subquery()

#to check if the user liked the content or not
#the column will have a 1 if the user did like, or a 0 if they didnt
def create_subquery_my_like_count_by_user(user_id):
    return session.query(Like.content_id, func.count().label('user_like_count')
                        ).filter(Like.user_id == user_id
                        ).group_by(Like.content_id).subquery()


#to check if the user reposted the content or not
#the column will have a 1 if the user did repost, or a 0 if they didnt
def create_subquery_my_reposts_count(user_visitor_id):
    return session.query(Post.content_id, func.count().label('user_repost_count')
                        ).filter(Post.user_poster_id == user_visitor_id, Post.user_creator_id != user_visitor_id,
                        ).group_by(Post.content_id
                        ).subquery()


def create_subquery_hashtags():
    """Create and return a subquery that retrieves hashtags per 'id_post'."""
    return (
        session.query(
            Hashtag.content_id, func.array_agg(Hashtag.hashtag).label("hashtags")
        )
        .group_by(Hashtag.content_id)
        .subquery()
    )

def create_did_i_like_column(subquery_user_like_count):
    return case(
        (subquery_user_like_count.c.user_like_count != 0, True),
        else_=False
    ).label('did_I_like')

def create_did_i_repost_column(subquery_user_repost_count):
    return case(
        (subquery_user_repost_count.c.user_repost_count != 0, True),
        else_=False
    ).label('did_I_repost')


def create_how_many_reposts(subquery_repost_count):
    #the -1 is to not count the original post as a repost
    return (subquery_repost_count.c.repost_count - 1).label('how_many_reposts')

def create_how_many_likes(subquery_likes_count):
    return subquery_likes_count.c.like_count.label('how_many_likes')
