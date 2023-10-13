"""
Archivo con algunas pruebas de la base de datos
"""
from sqlalchemy import and_, exists, or_, func
from sqlalchemy import desc
from sqlalchemy.orm import aliased
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.common_setup import *

# pylint: disable=C0114, W0401, W0614, E0401
from repository.tables.posts import Post, Like, Repost

# pylint: disable=C0114, W0401, W0614, E0401
from repository.tables.users import User, Following

def get_posts_from_users_followed_by_user_a(user_id_a):
    like_subquery = (
        session.query(Like.id_post, func.count(Like.id_post).label("like_count"))
        .group_by(Like.id_post)
        .subquery()
    )

    repost_subquery = (
        session.query(Repost.id_post, func.count(Repost.id_post).label("repost_count"))
        .group_by(Repost.id_post)
        .subquery()
    )

    posts = (
        session.query(
            Post,
            User,
            like_subquery.c.like_count,
            repost_subquery.c.repost_count,
        )
        .join(User, User.id == Post.user_id)
        .join(Following, Following.user_id == user_id_a)
        .filter(Post.user_id == Following.following_id)
        .outerjoin(like_subquery, Post.id == like_subquery.c.id_post)
        .outerjoin(repost_subquery, Post.id == repost_subquery.c.id_post)
        .order_by(Post.posted_at.desc())
        .all()
    )

    return posts


def get_post_from_user_b_to_user_a(user_id_a, user_id_b):
    user_b = aliased(User)

    like_subquery = (
        session.query(Like.id_post, func.count(Like.id_post).label("like_count"))
        .group_by(Like.id_post)
        .subquery()
    )

    repost_subquery = (
        session.query(Repost.id_post, func.count(Repost.id_post).label("repost_count"))
        .group_by(Repost.id_post)
        .subquery()
    )

    posts = (
        session.query(
            Post,
            User,
            like_subquery.c.like_count,
            repost_subquery.c.repost_count,
        )
        .join(User, User.id == Post.user_id)
        .filter(
            ((Post.user_id == user_id_b) &
            (user_b.is_public == True)) | 

            ( (Post.user_id == user_id_b) &
            exists().where(
                (Following.user_id == user_id_a) & (Following.following_id == user_id_b)
            ))
            
            )
        .outerjoin(like_subquery, Post.id == like_subquery.c.id_post)
        .outerjoin(repost_subquery, Post.id == repost_subquery.c.id_post)
        .order_by(Post.posted_at.desc())
        .all()
    )

    return posts


# ------------- Debug ---------------

def get_all_posts_with_details():

    like_subquery = (
        session.query(Like.id_post, func.count(Like.id_post).label("like_count"))
        .group_by(Like.id_post)
        .subquery()
    )

    repost_subquery = (
        session.query(Repost.id_post, func.count(Repost.id_post).label("repost_count"))
        .group_by(Repost.id_post)
        .subquery()
    )

    all_posts = (
        session.query(
            Post,
            User,
            like_subquery.c.like_count,
            repost_subquery.c.repost_count,
        )
        .join(User, User.id == Post.user_id)
        .outerjoin(like_subquery, Post.id == like_subquery.c.id_post)
        .outerjoin(repost_subquery, Post.id == repost_subquery.c.id_post)
        .order_by(Post.posted_at.desc())
        .all()
    )

    return all_posts