"""
Queries for getting posts, reposts, and all their info
"""
from sqlalchemy import or_, select
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


#query para levantar toda la info de posts y reposts antes de aplicar filtros
def get_posts_and_reposts(user_id):
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
    user_visitor_id, user_visited_id, oldest_date, amount
):
    """
    Get posts and reposts, with all their info, where the first id is the user that is
    visiting and the second id is the user that is being visited.

    Made for the profile, where visitor is the actual mobile user, and visited is another
    user that the owner of the token want to visit (could be themselves or someone else)
    """
    try:
        query_posts = get_posts_and_reposts(user_visitor_id)
        posts_id = (
            session.query(Post.post_id)
            .filter(Post.user_poster_id == user_visited_id)
            .distinct()
            .subquery()
        )
        query_final = query_posts.filter(Post.post_id.in_(posts_id)
                                ).filter(
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
                                        ).order_by(Post.created_at.desc()
                                        ).filter(Post.created_at < oldest_date
                                        ).limit(amount)

        results = query_final.all()
        if results is None:
            # a) the user visited is private and the user visitor doesnt follow them
            # b) the user doesnt have any posts
            if is_public(user_visited_id):
                raise UserIsPrivate()
            raise UserDoesntHavePosts()

        return results
    except Exception as error:
        raise DatabaseError from error


# #query para levantar sólo reposts de un id
# def get_reposts_from_user():
#     return



#query para levantar posts sólo según intereses
def get_posts_and_reposts_based_on_interests(user_id):

    query_posts = get_posts_and_reposts(user_id)
    
    subquery_hashtags_interests = create_subquery_hashtags_interests(user_id)
    subquery_followed_posts = create_subquery_posts_from_followd(user_id)

    subquery_results = session.query(subquery_hashtags_interests).all()
    print("Subquery Results:", subquery_results)

    #User2 = aliased(User)
    query_final = query_posts.filter(Post.content_id.in_(subquery_hashtags_interests),  # user is interested
                                    # ~Post.post_id.in_(subquery_followed_posts),     # no posts from followings
                                    # User.is_public == True,                         # the posts shown are public
                                    # Post.user_poster_id != user_id                 # they aren't the user's posts
                                    # Add other conditions here if needed
    )
                            #).filter(User.id == User2.id) #they are posts, not reposts
                            
    
    # Execute the query using your SQLAlchemy session
    results = query_final.all()
    if results is None:
        # no posts that are of interest to the user with that date
        raise UserDoesntHavePosts()

    return results





# #query para levantar posts y reposts sólo según followers
# def get_posts_and_reposts_based_on_followings():
#     return
