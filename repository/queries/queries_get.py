"""
Queries for getting posts, reposts, and all their info
"""
from sqlalchemy import or_
from sqlalchemy.orm import aliased

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.common_setup import *

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.queries_global import *

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.subqueries_get import *

# pylint: disable=C0114, W0401, W0614, E0401
from repository.tables.posts import *

# pylint: disable=C0114, W0401, W0614, E0401
from repository.tables.users import *

from repository.errors import UserIsPrivate, UserDoesntHavePosts, DatabaseError

PERCENTAGE_FOLLOWED = 0.7


def get_posts_and_reposts(user_id):
    """
    Returns query that gets all posts and reposts (with their respective info)
    and if this user liked or reposted the post
    """
    subquery_likes_count = create_subquery_likes_count()
    how_many_lies = create_how_many_likes(subquery_likes_count)

    subquery_repost_count = create_subquery_resposts_count()
    how_many_reposts = create_how_many_reposts(subquery_repost_count)

    subquery_my_likes_count = create_subquery_my_like_count_by_user(user_id)
    did_i_like_column = create_did_i_like_column(subquery_my_likes_count)

    subquery_my_reposts_count = create_subquery_my_reposts_count(user_id)
    did_i_repost_column = create_did_i_repost_column(subquery_my_reposts_count)

    hashtags_subquery = create_subquery_hashtags()

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
            how_many_lies,
            how_many_reposts,
            did_i_like_column,
            did_i_repost_column,
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
            subquery_my_likes_count,
            Post.content_id == subquery_my_likes_count.c.content_id,
            isouter=True,
        )
        .join(
            subquery_my_reposts_count,
            Post.content_id == subquery_my_reposts_count.c.content_id,
            isouter=True,
        )
        .join(
            hashtags_subquery,
            Post.content_id == hashtags_subquery.c.content_id,
            isouter=True,
        )
    )
    return query


# "Too many local variables"
# pylint: disable=R0914
def get_posts_and_reposts_from_users(
    user_visitor_id, user_visited_id, oldest_date, amount, only_reposts
):
    """
    Get posts and reposts, with all their info, where the first id is the user that is
    visiting and the second id is the user that is being visited.

    Made for the profile, where visitor is the actual mobile user, and visited is another
    user that the owner of the token want to visit (could be themselves or someone else)

    If only_reposts == True, then only reposts will be returned
    """
    query_posts = get_posts_and_reposts(user_visitor_id)
    posts_id = (
        session.query(Post.post_id)
        .filter(Post.user_poster_id == user_visited_id)
        .distinct()
        .subquery()
    )
    query_final = (
        query_posts.filter(Post.post_id.in_(posts_id))
        .filter(
            or_(
                # so that I can check my own profile with this query
                user_visited_id == user_visitor_id,
                # to check if im following the user
                Post.user_poster_id.in_(
                    session.query(Following.following_id).filter(
                        Following.user_id == user_visitor_id
                    )
                ),
                # to check if the user im visiting is public
                bool(is_public(user_visited_id)),
            )
        )
        .order_by(Post.created_at.desc())
        .filter(Post.created_at < oldest_date)
    )

    if only_reposts:
        query_final = query_final.filter(
            Post.user_poster_id != Post.user_creator_id  # to only get the reposts
        )

    query_final = query_final.limit(amount)

    results = query_final.all()
    if results is None:
        # a) the user visited is private and the user visitor doesnt follow them
        # b) the user doesnt have any posts
        if is_public(user_visited_id):
            raise UserIsPrivate()
        raise UserDoesntHavePosts()

    return results


# "Too many local variables"
# pylint: disable=R0914
def get_amount_posts_from_users(user_visitor_id, user_visited_id):
    """
    Get posts and reposts, with all their info, where the first id is the user that is
    visiting and the second id is the user that is being visited.

    Made for the profile, where visitor is the actual mobile user, and visited is another
    user that the owner of the token want to visit (could be themselves or someone else)

    If only_reposts == True, then only reposts will be returned
    """
    query_posts = get_posts_and_reposts(user_visitor_id)
    posts_id = (
        session.query(Post.post_id)
        .filter(
            Post.user_poster_id == user_visited_id,
            Post.user_creator_id == user_visited_id,
        )
        .distinct()
        .subquery()
    )
    query_final = (
        query_posts.filter(Post.post_id.in_(posts_id))
        .filter(
            or_(
                # so that I can check my own profile with this query
                user_visited_id == user_visitor_id,
                # to check if im following the user
                Post.user_poster_id.in_(
                    session.query(Following.following_id).filter(
                        Following.user_id == user_visitor_id
                    )
                ),
                # to check if the user im visiting is public
                bool(User.is_public),
            )
        )
        .order_by(Post.created_at.desc())
    )

    results = query_final.all()
    if results is None:
        # a) the user visited is private and the user visitor doesnt follow them
        # b) the user doesnt have any posts
        if is_public(user_visited_id):
            raise UserIsPrivate()
        raise UserDoesntHavePosts()

    return len(results)


def get_posts_and_reposts_based_on_interests(user_id, oldest_date):
    """
    Gets amount posts and reposts that the user_id might like, that are older than the oldest_date.
    The posts that the user might like are those that have at least one hashtag that matches one of
    the interests the user defined when signin up.

    This query will not return a post that the user might like if that post was made by another
    user that this users follows. That's to not repeat posts in the feed, since the query that
    gets posts and reposts from users this user follows might return that post as well.

    """
    query_posts = get_posts_and_reposts(user_id)

    subquery_hashtags_interests = create_subquery_hashtags_interests(user_id)
    subquery_followed_posts = create_subquery_posts_from_followd(user_id)

    query_final = (
        query_posts.filter(
            Post.content_id.in_(subquery_hashtags_interests),  # user is interested
            ~Post.post_id.in_(
                subquery_followed_posts
            ),  # no posts from users this user is following*
            # this is the check that works with == True
            # pylint: disable=C0121
            User.is_public == True,  # the posts shown are public
            Post.user_poster_id != user_id,  # they aren't the user's posts
        )
        .order_by(Post.created_at.desc())
        .filter(Post.created_at < oldest_date)
    )

    # * this is so that the other get function, that picks up the posts of the users
    # i do follow, doesnt get repetead posts.

    return query_final


def get_posts_and_reposts_based_on_followings(user_id, oldest_date):
    """
    Returns a query with posts and reposts from the users that this user_id follows,
    that are older than the oldest_date.
    """
    query_posts = get_posts_and_reposts(user_id)

    subquery_followed_posts = create_subquery_posts_from_followd(user_id)

    query_final = (
        query_posts.filter(Post.post_id.in_(subquery_followed_posts))
        .order_by(Post.created_at.desc())
        .filter(Post.created_at < oldest_date)
    )

    return query_final


def get_posts_and_reposts_feed(user_id, oldest_date, amount):
    """
    Obtains the posts for a user's feed, those of the users
    they follow and those that may interest them
    """
    query_posts_from_followed = get_posts_and_reposts_based_on_followings(
        user_id, oldest_date
    )
    query_posts_of_interest = get_posts_and_reposts_based_on_interests(
        user_id, oldest_date
    )

    num_posts_from_followed = int(amount * PERCENTAGE_FOLLOWED)
    num_posts_of_interest = int(amount * (1 - PERCENTAGE_FOLLOWED))

    posts = (
        query_posts_from_followed.limit(num_posts_from_followed)
        .union_all(query_posts_of_interest.limit(num_posts_of_interest))
        .order_by(Post.created_at.desc())
        .limit(amount)
    )

    return list(posts)


def get_reposts_of_users_content(user_id):
    """
    Gets all the reposts of all the posts made by this user

    It doesnt contain all the regular info that the other queries return.
    It only returns the post info (no user or content info)
    """
    query = (
        session.query(Post)
        # Only keep the reposts of the content created by the user_id
        .filter(Post.user_creator_id == user_id, Post.user_poster_id != user_id)
    )
    return query


def get_likes_of_users_content(user_id):
    """
    Gets all the likes from all the contents made by this user
    """
    query = (
        session.query(Like)
        # Keep the likes of the content created by the user_id
        .join(Post, Post.content_id == Like.content_id).filter(
            Post.user_creator_id == user_id
        )
    )
    return query


def get_statistics(user_id, from_date, to_date):
    """
    Get the statistics info of all the posts made by this user from the from_date
    to the to_date. If no posts are found, an exception will be launched.
    """

    query_posts = get_posts_and_reposts(user_id)
    query_only_my_posts = query_posts.filter(
        Post.user_creator_id == Post.user_poster_id, Post.user_poster_id == user_id
    ).filter(from_date <= Post.created_at, Post.created_at <= to_date)

    query_only_my_reposts = query_posts.filter(
        Post.user_creator_id != Post.user_poster_id, Post.user_poster_id == user_id
    ).filter(from_date <= Post.created_at, Post.created_at <= to_date)

    results_my_posts = query_only_my_posts.all()
    results_my_reposts = query_only_my_reposts.all()
    if not results_my_posts and not results_my_reposts:
        raise UserDoesntHavePosts()

    query_others_reposts = get_reposts_of_users_content(user_id).filter(
        from_date <= Post.created_at, Post.created_at <= to_date
    )
    results_others_reposts = query_others_reposts.all()

    query_likes = get_likes_of_users_content(user_id).filter(
        from_date <= Like.created_at, Like.created_at <= to_date
    )
    results_likes = query_likes.all()

    my_posts_count = len(results_my_posts)
    my_reposts_count = len(results_my_reposts)
    others_reposts_count = len(results_others_reposts)
    likes_count = len(results_likes) if results_likes is not None else 0

    statistics = {
        "my_posts_count": my_posts_count,
        "my_reposts_count": my_reposts_count,
        "others_reposts_count": others_reposts_count,
        "likes_count": likes_count,
    }

    return statistics


def get_posts_by_hashtags(user_id, hashtags, offset, amount):
    """
    This fuction gets all posts that have the hashtags passed as parameter
    :param hashtags: The hashtags to search for
    :param offset: The offset for pagination
    :param amount: The max amount of posts to return
    :param token: The authentication token.
    :return: A list of posts
    """
    query_posts = get_posts_and_reposts(user_id)
    subquery_hashtags = create_subquery_from_search_by_hashtags(hashtags)

    query_final = (
        query_posts.filter(Content.content_id.in_(subquery_hashtags)).filter(
            Post.user_poster_id == Post.user_creator_id
        )
        # pylint: disable=C0121
        .filter(User.is_public == True)
    )

    results = query_final.offset(offset).limit(amount)
    return results


def get_posts_by_text(user_id, text, offset, amount):
    """
    This fuction gets all posts that have the text passed as parameter
    :param text: The text to search for
    :param offset: The offset for pagination
    :param amount: The max amount of posts to return
    :param token: The authentication token.
    :return: A list of posts
    """
    query_posts = get_posts_and_reposts(user_id)

    query_final = (
        query_posts.filter(Post.user_poster_id == Post.user_creator_id)
        # pylint: disable=C0121
        .filter(User.is_public == True).filter(
            Content.text.ilike(f"%{text}%"),
        )
    )
    results = query_final.offset(offset).limit(amount)
    return results
