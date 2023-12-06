"""
Queries for getting posts, reposts, and all their info
"""

from sqlalchemy import case, func, or_
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


def create_subquery_my_favorites_count(user_id):
    """
    To check if the user favorited the content or not
    The column will have a 1 if the user did favorite, or a 0 if they didnt
    """
    return (
        # func.count is not callable, when it actually is
        # pylint: disable=E1102
        session.query(Favorite.content_id, func.count(1).label("user_favorite_count"))
        .filter(Favorite.user_id == user_id)
        .group_by(Favorite.content_id)
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


def create_subquery_mentions():
    """
    Create a subquery that retrieves mentions per 'content_id'.
    """
    subquery = (
        session.query(Mention.content_id, array_agg(User.username).label("mentions"))
        .join(User, Mention.user_mention_id == User.id)
        .group_by(Mention.content_id)
        .subquery()
    )
    return subquery


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


def create_did_i_put_favorite_column(subquery_user_favorite_count):
    """
    Create a subquery that checks if the value in the user_favorite_count
    column is 0 (--> the user didnt favorite the content) or 1
    (--> the user did favorite the content), and replaces each value with
    a False or True respetively
    """
    return case(
        (subquery_user_favorite_count.c.user_favorite_count != 0, True), else_=False
    ).label("did_I_favorite")


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


### chequear, la acabo de cambiar
def create_subquery_posts_from_followd(user_id):
    """
    Create subquery that returns all the posts from users that the user_id follows
    """
    return (
        session.query(Post.post_id)
        .outerjoin(
            Following,
            or_(
                Following.following_id == Post.user_poster_id,
                Post.user_poster_id == user_id,
            ),
        )
        .filter(or_(Following.user_id == user_id, Post.user_poster_id == user_id))
        .distinct()
        .subquery()
    )


def create_subquery_from_search_by_hashtags(hashtags):
    """
    Create subquery that returns all the contents ids
    """
    return (
        session.query(Hashtag.content_id)
        .filter(Hashtag.hashtag.in_(hashtags))
        .distinct()
        .subquery()
    )


def create_subquery_get_shared_location(user_id):
    """
    Create subquery that returns the location of the user_id
    """
    user_location = session.query(User.location).filter_by(id=user_id).scalar()
    return case((User.location == user_location, 1), else_=0).label("location_shared")


def create_subquery_get_followed_users(user_id):
    """
    Subquery to get users followed by the given user.
    """
    return (
        session.query(Following.following_id)
        .filter(Following.user_id == user_id)
        .subquery()
    )


def create_subquery_followings(user_id):
    """
    Create subquery that returns all the users that the user_id follows
    """
    return (
        session.query(Following.following_id)
        .filter(Following.user_id == user_id)
        .subquery()
    )


def create_subquery_followings_of_my_followings(subquery_following):
    """
    Create subquery that returns the followings of those I follow
    """
    return (
        session.query(Following.following_id.label("friend_of_friend"))
        .filter(Following.user_id.in_(subquery_following))
        .subquery()
    )


def create_subquery_common_followings_count(
    user_id, subquery_followings_of_my_followings
):
    """
    Create subquery that returns the amount of common followings
    """
    return (
        session.query(
            User.id.label("id"),
            # func.count is not callable, when it actually is
            # pylint: disable=E1102
            func.count(subquery_followings_of_my_followings.c.friend_of_friend).label(
                "friend_of_friend_count"
            ),
        )
        .outerjoin(
            subquery_followings_of_my_followings,
            User.id == subquery_followings_of_my_followings.c.friend_of_friend,
        )
        .filter(User.id != user_id)
        .group_by(User.id)
        .subquery()
    )


def create_subquery_get_interests(user_id):
    """
    Create subquery that returns all the interests that the user_id has
    """
    return (
        session.query(Interests.interest)
        .filter(Interests.user_id == user_id)
        .subquery()
    )


def create_subquery_get_posts_that_match_my_interests(subquery_interests):
    """
    Create subquery that returns all posts that have at least one hashtag
    """
    return (
        session.query(Post.user_creator_id, Post.post_id.label("interest_posts"))
        .join(Hashtag, Post.content_id == Hashtag.content_id)
        .filter(Hashtag.hashtag.in_(subquery_interests))
        .subquery()
    )


def create_subquery_get_posts_that_match_my_interests_count(
    user_id, subquery_interest_posts
):
    """
    Create subquery that returns the amount of posts that
    have at least one hashtag
    """
    return (
        session.query(
            User.id,
            # func.count is not callable, when it actually is
            # pylint: disable=E1102
            func.count(subquery_interest_posts.c.interest_posts).label(
                "interest_posts_count"
            ),
        )
        .outerjoin(
            subquery_interest_posts,
            User.id == subquery_interest_posts.c.user_creator_id,
        )
        .filter(User.id != user_id)
        .group_by(User.id)
        .subquery()
    )


def create_subquery_get_likes_that_match_my_interests(subquery_interests):
    """
    Create subquery that returns all likes that have at least one hashtag
    """
    return (
        session.query(Like.user_id, Like.content_id.label("interest_likes"))
        .join(Post, Post.content_id == Like.content_id)
        .join(Hashtag, Post.content_id == Hashtag.content_id)
        .filter(Post.user_creator_id == Post.user_poster_id)
        .filter(Hashtag.hashtag.in_(subquery_interests))
        .subquery()
    )


def create_subquery_get_likes_that_match_my_interests_count(
    user_id, subquery_interest_likes
):
    """
    Create subquery that returns the amount of likes that
    """
    return (
        session.query(
            User.id,
            # func.count is not callable, when it actually is
            # pylint: disable=E1102
            func.count(subquery_interest_likes.c.interest_likes).label(
                "interest_likes"
            ),
        )
        .outerjoin(
            subquery_interest_likes, User.id == subquery_interest_likes.c.user_id
        )
        .filter(User.id != user_id)
        .group_by(User.id)
        .subquery()
    )
