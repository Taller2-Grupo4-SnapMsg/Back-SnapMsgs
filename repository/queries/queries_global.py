"""
Archivo con algunas pruebas de la base de datos
"""
from sqlalchemy import and_, func, literal, select
from sqlalchemy import desc
from sqlalchemy.orm import aliased

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.common_setup import *

# pylint: disable=C0114, W0401, W0614, E0401
from repository.tables.posts import Post, Like, Repost, Hashtag

# pylint: disable=C0114, W0401, W0614, E0401
from repository.tables.users import User, Following, Interests

def get_post_for_user_feed(user_id_a, n, date) :
    post_that_I_follow = get_posts_from_users_followed_by_user_a(user_id_a, int(n * 0.7), date)
    post_of_my_interest = get_public_posts_user_is_interested_in(user_id_a, int(n * 0.3), date)
    return post_that_I_follow.extend(post_of_my_interest)


def get_public_posts_user_is_interested_in(user_id, amount, oldest_date) :
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
    interests_alias = aliased(Interests)
    posts = (
        session.query(
            Post,
            User,
            like_subquery.c.like_count,
            repost_subquery.c.repost_count,
        )
        .join(Hashtag, Hashtag.id_post == Post.id)
        .join(interests_alias, interests_alias.interest == Hashtag.hashtag)
        .filter(interests_alias.user_id == user_id)
        .join(User, User.id == Post.user_id)
        .outerjoin(like_subquery, Post.id == like_subquery.c.id_post)
        .outerjoin(repost_subquery, Post.id == repost_subquery.c.id_post)

        .outerjoin(Following, and_(Following.user_id == user_id, Following.following_id == User.id))
        .filter(Following.user_id == None)

        #.distinct(Post.id)
        #.order_by(Post.id) 

        .filter(User.is_public == True)
        .filter(Post.user_id != user_id)
        .where(Post.posted_at < oldest_date)
        .order_by(desc(Post.posted_at))
        .limit(amount)
    )

    return posts

def get_posts_from_users_followed_by_user_a(user_id_a, n, date):
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
        .filter(Post.posted_at < date)
        .order_by(Post.posted_at.desc())
        .limit(n)
    )

    return posts

def get_posts_and_reposts_from_users_followed_by_user_a(user_id_a, n, date):
    like_subquery = (
        session.query(Like.id_post, func.count(Like.id_post).label("like_count"))
        .group_by(Like.id_post)
        .subquery()
    )

    repost_subquery = (
        session.query(
            Repost.id_post,
            func.count(Repost.id_post).label("repost_count"),
            Repost.user_id.label("repost_user_id")
        )
        .group_by(Repost.id_post, Repost.user_id)
        .subquery()
    )

    # Consulta para obtener los posts originales (no reposts)
    original_posts = (
        session.query(
            Post,
            User,
            like_subquery.c.like_count,
            repost_subquery.c.repost_count,
            #literal(None).label("user_id_repost") 
        )
        .join(User, User.id == Post.user_id)
        .join(Following, Following.user_id == user_id_a)
        .filter(Post.user_id == Following.following_id)
        .outerjoin(like_subquery, Post.id == like_subquery.c.id_post)
        .outerjoin(repost_subquery, Post.id == repost_subquery.c.id_post)
        .filter(Post.posted_at < date)
    )

    # Consulta para obtener los reposts y sus respectivos usuarios que los hicieron
    reposts = (
        session.query(
            Post,
            User,
            like_subquery.c.like_count,
            repost_subquery.c.repost_count,
            repost_subquery.c.repost_user_id.label("user_id_repost")
        )
        .join(User, User.id == Post.user_id)
        .join(Repost, Repost.id_post == Post.id)
        .outerjoin(like_subquery, Post.id == like_subquery.c.id_post)
        .outerjoin(repost_subquery, Post.id == repost_subquery.c.id_post)
        #.outerjoin(repost_subquery, Post.id == repost_subquery.c.id_post)
        #.join(User, User.id == repost_subquery.c.repost_user_id)
        #.join(Post, Post.id == repost_subquery.c.id_post)
        #.filter(repost_subquery.c.repost_user_id == user_id_a)
        .filter(Post.posted_at < date)
    )

    # Combinar los resultados de posts originales y reposts
    combined_posts = original_posts.union_all(reposts)

    # Ordenar y limitar la consulta
    posts = combined_posts.order_by(Post.posted_at.desc()).limit(n)

    #print("LLEGA A TERMINAR LA QUERIE")
    #print("REPOST")
    #print(reposts)
    #print("POST")
    #print(posts)
    return posts


def is_following(user_id, user_id_to_check_if_following):
    """
    Returns True if the user with the given id is following the user with the given id.
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


def get_post_from_user_b_to_user_a(user_id_a, user_id_b):
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

    posts = []
    if (is_following(user_id_a, user_id_b) or is_public(user_id_b) or (user_id_a == user_id_b) ):
        posts = (
            session.query(
                Post,
                User,
                like_subquery.c.like_count,
                repost_subquery.c.repost_count,
            )
            .join(User, User.id == Post.user_id)
            .filter(Post.user_id == user_id_b)
            .outerjoin(like_subquery, Post.id == like_subquery.c.id_post)
            .outerjoin(repost_subquery, Post.id == repost_subquery.c.id_post)
            .order_by(Post.posted_at.desc())
            .all()
        )

    return posts

#probar
def get_post_by_id_global(user_id, post_id):
    like_subquery = (
        session.query(Like.id_post, 
                      func.count(Like.id_post)
                      .label("like_count"))
        .group_by(Like.id_post)
        .subquery()
    )

    repost_subquery = (
        session.query(Repost.id_post, 
                      func.count(Repost.id_post)
                      .label("repost_count"))
        .group_by(Repost.id_post)
        .subquery()
    )

    post = session.query(Post, User).filter(Post.id == post_id).first()
    if (is_following(user_id, post.user_id) or 
                    is_public(post.user_id) or 
                    (user_id == post.user_id) ):
        posts = (
            session.query(
                Post,
                User,
                like_subquery.c.like_count,
                repost_subquery.c.repost_count,
            )
            .join(User, User.id == Post.user_id)
            .filter(Post.id == post.id)
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

def get_visible_posts_for_user(user_a_id, user_b_id):
    # Subquery para contar likes
    likes_subquery = (
        session.query(func.count(Like.id))
        .filter(Like.id_post == Post.id)
        .label("like_count")
    )

    # Subquery para contar reposts
    reposts_subquery = (
        session.query(func.count(Repost.id))
        .filter(Repost.id_post == Post.id)
        .label("repost_count")
    )

#no va, por si algo falla
def get_public_posts_user_is_interested_in2(user_id, amount, oldest_date) :
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
    query = (
        select(
            Post,
            User,
            like_subquery.c.like_count,
            repost_subquery.c.repost_count
        )
        .select_from(
            Post.__table__
            .join(User, User.id == Post.user_id)
            .join(Interests, Interests.user_id == user_id)
            .join(Hashtag, Interests.interest == Hashtag.hashtag)
            #.join(Post, Post.id == Hashtag.id_post)
            .outerjoin(like_subquery, Post.id == like_subquery.c.id_post)
            .outerjoin(repost_subquery, Post.id == repost_subquery.c.id_post)

        )        
        .outerjoin(Following, and_(Following.user_id == user_id, Following.following_id == User.id))
        .filter(Following.user_id == None)

        .distinct(Post.id)
        .order_by(Post.id) 

        .filter(User.is_public == True)
        .filter(Post.user_id != user_id)
        .where(Post.posted_at < oldest_date)
        .order_by(desc(Post.posted_at))
        .limit(amount)
    )

    return session.execute(query)
