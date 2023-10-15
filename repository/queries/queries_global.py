"""
Archivo con algunas pruebas de la base de datos
"""
from sqlalchemy import and_, func, literal_column, or_, desc
from sqlalchemy.orm import aliased

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.common_setup import *

# pylint: disable=C0114, W0401, W0614, E0401
from repository.tables.posts import Post, Like, Repost, Hashtag

# pylint: disable=C0114, W0401, W0614, E0401
from repository.tables.users import User, Following, Interests

def create_like_subquery(session):
    """Create and return a subquery that counts 'Likes' per 'id_post'."""
    return (
        session.query(Like.id_post, func.count(Like.id_post)
                      .label("like_count"))
        .group_by(Like.id_post)
        .subquery()
    )

def create_repost_subquery(session):
    """Create and return a subquery that counts 'Reposts' per 'id_post'."""
    return (
        session.query(Repost.id_post, func.count(Repost.id_post)
                      .label("repost_count"))
        .group_by(Repost.id_post)
        .subquery()
    )

def create_hashtags_subquery(session):
    """Create and return a subquery that retrieves hashtags per 'id_post'."""
    return (
        session.query(Hashtag.id_post, func.array_agg(Hashtag.hashtag)
                      .label("hashtags"))
        .group_by(Hashtag.id_post)
        .subquery()
    )

def create_repost_subquery_with_repost_user(session):
    """
    Create and return a subquery that counts the number of 
    'Reposts' per 'id_post' and includes the 'user_id' 
    of the users who performed the reposts.
    """
    return (
        session.query(
            Repost.id_post,
            func.count(Repost.id_post).label("repost_count"),
            Repost.user_id.label("repost_user_id")
        )
        .group_by(Repost.id_post, Repost.user_id)
        .subquery()
    )

def is_following(user_id, user_id_to_check_if_following):
    """
    Returns True if the user with the given id is following 
    the user with the given id.
    """
    following = (
        session.query(Following)
        .filter(Following.user_id == user_id)
        .filter(Following.following_id == user_id_to_check_if_following)
        .first()
    )
    return following is not None

def is_public(user_id):
    """
    Returns True if the user is public.
    """
    public = (
        session.query(User)
        .filter(User.id == user_id)
        .filter(User.is_public == True)
        .first()
    )
    return public is not None

def get_post_from_user_b_to_user_a(user_id_a, user_id_b, n, date):
    """
    To get posts from a user's profile.

    Points to consider:

    user b: user from whom I want to see the posts.
    user a: user I want to see user b's posts.

    If user a and user b are the same:
    you are wanting to see your profile and it lets you.
    
    In case of different users:
    It will show you user_b's posts:
    - if they are followed
    - if user b is public
    It will show you the reposts made by user b if user a meets 
    the conditions mentioned above and:
    - if you follow the person who made the original post
    - the person who made the original post is public
    """
    like_subquery = create_like_subquery(session)
    repost_subquery = create_repost_subquery(session)
    hashtags_subquery = create_hashtags_subquery(session)

    posts = []
    post_user_alias = aliased(User)
    user_who_reposted_alias = aliased(User)
    user_who_reposted_alias_ = aliased(User)

    if (is_following(user_id_a, user_id_b) or is_public(user_id_b) 
        or (user_id_a == user_id_b) ):
        original_posts = (
            session.query(
                Post,
                User,
                user_who_reposted_alias_,
                like_subquery.c.like_count,
                repost_subquery.c.repost_count,
                hashtags_subquery.c.hashtags,
                literal_column("false").label("is_repost")
            )
            .join(User, User.id == Post.user_id)
            .filter(Post.user_id == user_id_b)
            .outerjoin(like_subquery, Post.id == like_subquery.c.id_post)
            .outerjoin(repost_subquery, Post.id == repost_subquery.c.id_post)
            .outerjoin(hashtags_subquery, Post.id == hashtags_subquery.c.id_post)

            .distinct(Post.id)
            .order_by(Post.id) 

            .order_by(Post.posted_at.desc())
            .filter(Post.posted_at < date)
        )
        reposts = (
            session.query(
                Post,
                post_user_alias,  # Usuario que hizo el post original
                user_who_reposted_alias,  # Usuario que hizo el repost
                like_subquery.c.like_count,
                repost_subquery.c.repost_count,
                hashtags_subquery.c.hashtags,
                literal_column("true").label("is_repost")
            )
            .select_from(
                Repost.__table__
                    .join(Post, Post.id == Repost.id_post)
                    .join(post_user_alias, post_user_alias.id == Post.user_id)
                    .join(user_who_reposted_alias, 
                          user_who_reposted_alias.id == Repost.user_id)

                    .outerjoin(repost_subquery, 
                                Post.id == repost_subquery.c.id_post)
                    .outerjoin(like_subquery, 
                                Post.id == like_subquery.c.id_post)
                    .outerjoin(hashtags_subquery, 
                                Post.id == hashtags_subquery.c.id_post)
                )
            .filter(or_(post_user_alias.is_public.is_(True), 
                    is_following(user_id_a, post_user_alias.id)))
            .filter(user_who_reposted_alias.id == user_id_b)
            .filter(Post.posted_at < date)
        )
    combined_posts = original_posts.union_all(reposts)

    posts = combined_posts.order_by(Post.posted_at.desc()).limit(n)

    return posts

def get_post_for_user_feed(user_id_a, n, date) :
    """
    Obtains the posts for a user's feed, those of the users 
    they follow and those that may interest them
    """
    post_that_I_follow = list(get_posts_from_users_followed_by_user(
                        user_id_a, int(n * 0.7), date))
    post_of_my_interest = list(get_public_posts_user_is_interested_in(
                        user_id_a, int(n * 0.3), date))
    return post_that_I_follow + post_of_my_interest


def get_public_posts_user_is_interested_in(user_id, amount, oldest_date) :
    """
    Obtains public posts that may interest the user
    """
    like_subquery = create_like_subquery(session)
    repost_subquery = create_repost_subquery(session)
    hashtags_subquery = create_hashtags_subquery(session)

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
            literal_column("false").label("is_repost")
        )
        .join(Hashtag, Hashtag.id_post == Post.id)
        .join(interests_alias, interests_alias.interest == Hashtag.hashtag)
        .filter(interests_alias.user_id == user_id)
        .join(User, User.id == Post.user_id)
        .outerjoin(like_subquery, Post.id == like_subquery.c.id_post)
        .outerjoin(repost_subquery, Post.id == repost_subquery.c.id_post)
        .outerjoin(hashtags_subquery, Post.id == hashtags_subquery.c.id_post)

        .outerjoin(Following, and_(Following.user_id == user_id, 
                                   Following.following_id == User.id))
        .filter(Following.user_id == None)
        #.filter(not is_following(user_id, User.id))
 
        .distinct(Post.posted_at)

        .filter(User.is_public == True)
        .filter(Post.user_id != user_id)
        .filter(Post.posted_at < oldest_date)
        .order_by(desc(Post.posted_at))
        .limit(amount)
    )

    return posts


def get_posts_from_users_followed_by_user(user_id, n, date):
    """
    Gets posts from users I follow
    """
    like_subquery = create_like_subquery(session)
    repost_subquery = create_repost_subquery_with_repost_user(session)
    hashtags_subquery = create_hashtags_subquery(session)

    post_alias = aliased(Post)
    repost_alias = aliased(Post)
    post_user_alias = aliased(User)
    user_who_reposted_alias = aliased(User)
    user_who_reposted_alias_ = aliased(User)

    original_posts = (
        session.query(
            post_alias,
            User,
            user_who_reposted_alias_,
            like_subquery.c.like_count,
            repost_subquery.c.repost_count,
            hashtags_subquery.c.hashtags,
            literal_column("false").label("is_repost")
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
            literal_column("true").label("is_repost")
        )
        .select_from(
            Repost.__table__
                .join(repost_alias, repost_alias.id == Repost.id_post)
                .join(post_user_alias,
                      post_user_alias.id == repost_alias.user_id)
                .join(user_who_reposted_alias,
                      user_who_reposted_alias.id == Repost.user_id)

                .outerjoin(repost_subquery,
                           repost_alias.id == repost_subquery.c.id_post)
                .outerjoin(like_subquery,
                           repost_alias.id == like_subquery.c.id_post)
            )
        .distinct(repost_alias.id)
        .filter(repost_alias.posted_at < date)
        .filter(or_(post_user_alias.is_public.is_(True), 
                is_following(user_id, post_user_alias.id)))
        #.filter(repost_alias.user_id != user_id)
    )
    combined_posts = original_posts.union_all(reposts)

    posts = combined_posts.order_by(Post.posted_at.desc()).limit(n)
    return posts

def get_post_by_id_global(user_id, post_id):
    """Gets a post by id"""
    like_subquery = create_like_subquery(session)
    repost_subquery = create_repost_subquery(session)
    hashtags_subquery = create_hashtags_subquery(session)

    user_who_reposted_alias_ = aliased(User)

    post = session.query(Post).filter(Post.id == post_id).first()
    if (is_following(user_id, post.user_id) or 
                    is_public(post.user_id) or 
                    (user_id == post.user_id) ):
        posts = (
            session.query(
                Post,
                User,
                user_who_reposted_alias_,
                like_subquery.c.like_count,
                repost_subquery.c.repost_count,
                hashtags_subquery.c.hashtags,
                literal_column("false").label("is_repost")
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
