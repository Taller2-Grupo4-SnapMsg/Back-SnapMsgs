"""
Queries for getting posts, reposts, and all their info
"""

from sqlalchemy import case, func

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


# Get posts and reposts, with all their info, where the first id is the user that is
# visiting and the second id is the user that is being visited.

# Made for the profile, where visitor is the actual mobile user, and visited is another
# user that the owner of the token want to visit (could be themselves or someone else)
def get_posts_and_reposts_from_users(user_visitor_id: int, user_visited_id: int):
    try:
        print(f"El visitor_id es: {user_visitor_id} y el visited_id es {user_visited_id}")
        subquery_likes_count = create_subquery_likes_count()
        how_many_lies = create_how_many_likes(subquery_likes_count)

        subquery_repost_count = create_subquery_resposts_count()
        how_many_reposts = create_how_many_reposts(subquery_repost_count)

        subquery_my_likes_count = create_subquery_my_like_count_by_user(user_visited_id)
        did_i_like_column = create_did_i_like_column(subquery_my_likes_count)
        
        subquery_my_reposts_count = create_subquery_my_reposts_count(user_visited_id)
        did_i_repost_column = create_did_i_repost_column(subquery_my_reposts_count)

        hashtags_subquery = create_subquery_hashtags()
        posts_id = session.query(Post.post_id).filter(Post.user_poster_id == user_visited_id).distinct().subquery()

        User2 = aliased(User)
        query = session.query(
            Post,
            Content,
            User.id.label('user_poster_id'),
            User.name.label('user_poster_name'),
            User.is_public.label('user_poster_is_public'),
            User2.id.label('user_creator_id'),
            User2.name.label('user_creator_name'),
            User2.is_public.label('user_creator_is_public'),
            hashtags_subquery.c.hashtags,
            how_many_lies,
            how_many_reposts, 
            did_i_like_column,
            did_i_repost_column,
        ).join(Content, Post.content_id == Content.content_id
        ).join(User, User.id == Post.user_poster_id
        ).join(User2, User2.id == Post.user_creator_id
        ).join(subquery_likes_count, Post.content_id == subquery_likes_count.c.content_id, isouter=True
        ).join(subquery_repost_count, Post.content_id == subquery_repost_count.c.content_id, isouter=True
        ).join(subquery_my_likes_count, Post.content_id == subquery_my_likes_count.c.content_id, isouter=True
        ).join(subquery_my_reposts_count, Post.content_id == subquery_my_reposts_count.c.content_id, isouter=True 
        ).join(hashtags_subquery, Post.content_id == hashtags_subquery.c.content_id, isouter=True
        ).filter(Post.post_id.in_(posts_id)
        ).filter(
            or_(
                #so that I can check my own profile with this query
                user_visited_id == user_visitor_id,
                #to check if im following the user  
                Post.user_poster_id.in_(session.query(Following.following_id).filter(Following.user_id == user_visitor_id)),
                #to check if the user im visiting is public
                User.is_public == True
            )
        )

        results = query.all()
        if results is None:
            #a) the user visited is private and the user visitor doesnt follow them
            #b) the user doesnt have any posts
            if is_public(user_visited_id):
                raise UserIsPrivate()
            else:
                UserDoesntHavePosts()
        
        return results
    except Exception as error:
        raise DatabaseError from error


#query para levantar sólo reposts de un id
def get_reposts_from_user():
    return

#query para levantar toda la info de posts y reposts antes de aplicar filtros
def get_posts_and_reposts():
    return

#query para levantar posts y reposts sólo según intereses
def get_posts_and_reposts_based_on_interests():
    return


#query para levantar posts y reposts sólo según followers
def get_posts_and_reposts_based_on_followings():
    return