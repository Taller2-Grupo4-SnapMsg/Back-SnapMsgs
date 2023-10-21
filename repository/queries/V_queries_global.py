"""
Archivo con algunas pruebas de la base de datos
"""
from sqlalchemy import and_, literal_column, or_, desc
from sqlalchemy import func
from sqlalchemy.orm import aliased

from repository.errors import PostNotFound

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.common_setup import *

# pylint: disable=C0114, W0401, W0614, E0401
from repository.tables.posts import Post, Like, Hashtag

# pylint: disable=C0114, W0401, W0614, E0401
from repository.tables.users import User, Following, Interests


# pylint: disable=E1102
def create_like_subquery():
    """Create and return a subquery that counts 'Likes' per 'id_post'."""
    return (
        session.query(Like.id_post, func.count(Like.id_post).label("like_count"))
        .group_by(Like.id_post)
        .subquery()
    )

def get_post_for_user_feed(user_id, amount, date):
    """
    Obtains the posts for a user's feed, those of the users
    they follow and those that may interest them
    """
    posts_from_followed = _get_posts_from_users_followed_by_user(
        user_id, date
    ).order_by(Post.posted_at.desc())
    posts_of_interest = _get_public_posts_user_is_interested_in(user_id, date)
    num_posts_from_followed = int(amount * 0.7)
    num_posts_of_interest = int(amount * 0.3)

    combined_posts = posts_from_followed.limit(num_posts_from_followed).union_all(
        posts_of_interest.limit(num_posts_of_interest)
    )
    posts = combined_posts.order_by(Post.posted_at.desc()).limit(amount)
    return list(posts)

def get_posts_from_users_followed_by_user(user_id, amount, date):
    """
    Gets posts from users I follow
    """
    posts_from_followed = _get_posts_from_users_followed_by_user(user_id, date)
    posts = posts_from_followed.order_by(Post.posted_at.desc()).limit(amount)
    return posts

def get_public_posts_user_is_interested_in(user_id, amount, date):
    """
    Obtains public posts that may interest the user
    """
    posts_of_interest = _get_public_posts_user_is_interested_in(user_id, date)
    posts = posts_of_interest.order_by(Post.posted_at.desc()).limit(amount)
    return posts

def _get_public_posts_user_is_interested_in(user_id, oldest_date):
    """
    Obtains public posts that may interest the user
    """
    like_subquery = create_like_subquery()
    repost_subquery = create_repost_subquery()
    hashtags_subquery = create_hashtags_subquery()

    user_who_reposted_alias_ = aliased(User)
    interests_alias = aliased(Interests)

    posts = (
        session.query(
            Post,
            User,
            user_who_reposted_alias_,
            like_subquery.c.like_count,
            repost_subquery.c.repost_count,
            hashtags_subquery.c.hashtags,
            literal_column("false").label("is_repost"),
        )
        .join(Hashtag, Hashtag.id_post == Post.id)
        .join(interests_alias, interests_alias.interest == Hashtag.hashtag)
        .filter(interests_alias.user_id == user_id)
        .join(User, User.id == Post.user_id)
        .outerjoin(like_subquery, Post.id == like_subquery.c.id_post)
        .outerjoin(repost_subquery, Post.id == repost_subquery.c.id_post)
        .outerjoin(hashtags_subquery, Post.id == hashtags_subquery.c.id_post)
        .outerjoin(
            Following,
            and_(Following.user_id == user_id, Following.following_id == User.id),
        )
        # pylint: disable=C0121
        .filter(Following.user_id == None)
        .distinct(Post.posted_at)
        # pylint: disable=C0121
        .filter(User.is_public == True)
        .filter(Post.user_id != user_id)
        .filter(Post.posted_at < oldest_date)
        .order_by(desc(Post.posted_at))
        # .limit(amount)
    )

    return posts

# pylint: disable=R0914
def _get_posts_from_users_followed_by_user(user_id, date):
    """
    Gets posts from users I follow
    """
    like_subquery = create_like_subquery()
    repost_subquery = create_repost_subquery_with_repost_user()
    hashtags_subquery = create_hashtags_subquery()

    post_alias = aliased(Post)
    repost_alias = aliased(Post)
    post_user_alias = aliased(User)
    user_who_reposted_alias = aliased(User)
    user_who_reposted_alias_ = aliased(User)

    followers_subquery = (
        session.query(Following.following_id)
        .filter(Following.user_id == User.id)  # Reemplaza con la variable real
        .subquery()
    )

    subquery = (
        session.query(Following)
        .filter(Following.user_id == user_id)
        .filter(Following.following_id == post_user_alias.id)
        .exists()
    )

    subquery_follow = (
        session.query(Following)
        .filter(Following.user_id == user_id)
        .filter(Following.following_id == user_who_reposted_alias.id)
        .exists()
    )

    original_posts = (
        session.query(
            post_alias,
            User,
            user_who_reposted_alias_,
            like_subquery.c.like_count,
            repost_subquery.c.repost_count,
            hashtags_subquery.c.hashtags,
            literal_column("false").label("is_repost"),
        )
        .join(User, User.id == post_alias.user_id)
        .join(Following, Following.user_id == user_id)
        .filter(post_alias.user_id == Following.following_id)
        .outerjoin(like_subquery, post_alias.id == like_subquery.c.id_post)
        .outerjoin(repost_subquery, post_alias.id == repost_subquery.c.id_post)
        .distinct(post_alias.id)
        .filter(post_alias.posted_at < date)
    )

    reposts = (
        session.query(
            repost_alias,
            post_user_alias,
            user_who_reposted_alias,
            like_subquery.c.like_count,
            repost_subquery.c.repost_count,
            hashtags_subquery.c.hashtags,
            literal_column("true").label("is_repost"),
        )
        .select_from(
            Repost.__table__.join(repost_alias, repost_alias.id == Repost.id_post)
            .join(post_user_alias, post_user_alias.id == repost_alias.user_id)
            .join(user_who_reposted_alias, user_who_reposted_alias.id == Repost.user_id)
            .outerjoin(repost_subquery, repost_alias.id == repost_subquery.c.id_post)
            .outerjoin(like_subquery, repost_alias.id == like_subquery.c.id_post)
            .join(
                followers_subquery,
                followers_subquery.c.following_id == user_who_reposted_alias.id,
            )
        )
        # .filter(user_who_reposted_alias.id.in_(followers_subquery))
        .distinct(repost_alias.id)
        .filter(repost_alias.posted_at < date)
        .filter(or_(post_user_alias.is_public.is_(True), subquery))
        .filter(subquery_follow)
        # .filter(repost_alias.user_id != user_id)
    )
    combined_posts = original_posts.union_all(reposts)

    # posts = combined_posts.order_by(Post.posted_at.desc()).limit(amount)
    return combined_posts

def get_post_by_id_global(user_id, post_id):
    """Gets a post by id"""
    like_subquery = create_like_subquery()
    repost_subquery = create_repost_subquery()
    hashtags_subquery = create_hashtags_subquery()

    user_who_reposted_alias_ = aliased(User)

    post = session.query(Post).filter(Post.id == post_id).first()

    if (
        is_following(user_id, post.user_id)
        or is_public(post.user_id)
        or (user_id == post.user_id)
    ):
        posts = (
            session.query(
                Post,
                User,
                user_who_reposted_alias_,
                like_subquery.c.like_count,
                repost_subquery.c.repost_count,
                hashtags_subquery.c.hashtags,
                literal_column("false").label("is_repost"),
            )
            .join(User, User.id == Post.user_id)
            .filter(Post.id == post.id)
            .outerjoin(like_subquery, Post.id == like_subquery.c.id_post)
            .outerjoin(repost_subquery, Post.id == repost_subquery.c.id_post)
            .outerjoin(hashtags_subquery, Post.id == hashtags_subquery.c.id_post)
            .distinct(Post.id)
            .one()
        )

        return posts
    raise PostNotFound()
