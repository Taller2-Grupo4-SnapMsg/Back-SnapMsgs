"""
Archivo con algunas pruebas de la base de datos
"""
from sqlalchemy import and_, exists, literal_column, or_, func, select
from sqlalchemy import desc
from sqlalchemy.orm import aliased
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.common_setup import *

# pylint: disable=C0114, W0401, W0614, E0401
from repository.tables.posts import Post, Like, Repost, Hashtag

# pylint: disable=C0114, W0401, W0614, E0401
from repository.tables.users import User, Following, Interests

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

#no va, por si algo falla
def get_public_posts_user_is_interested_in3(user_id, amount, oldest_date) :
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
    i = aliased(Interests)
    h = aliased(Hashtag)
    p2 = aliased(Post)
    u = aliased(User)

    posts = (
        session.query(
            Post,
            User,
            like_subquery.c.like_count,
            repost_subquery.c.repost_count
        )
        .join(i, i.user_id == user_id)
        .join(h, i.interest == h.hashtag)
        .join(p2, p2.id == h.id_post)
        .filter(p2.posted_at < oldest_date)
        .join(u, u.id == p2.user_id)
        .group_by(Post.id, User.id)
        .filter(u.is_public == True)
        .outerjoin(like_subquery, Post.id == like_subquery.c.id_post)
        .outerjoin(repost_subquery, Post.id == repost_subquery.c.id_post)
        .order_by(desc(Post.posted_at))
        .limit(amount)
    )

    return posts

    

def get_post_for_user_feed(user_id_a, n, date) :
    post_that_I_follow = get_posts_from_users_followed_by_user_a(user_id_a, int(n * 0.7), date)
    post_of_my_interest = get_public_posts_user_is_interested_in(user_id_a, int(n * 0.3), date)
    post_that_I_follow.extend(post_of_my_interest)

#no va, por si algo falla
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
    i = aliased(Interests)
    h = aliased(Hashtag)
    p2 = aliased(Post)
    u = aliased(User)

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
            .join(i, i.user_id == user_id)
            .join(h, i.interest == h.hashtag)
            .join(p2, p2.id == h.id_post)
            #.join(u, p2.user_id == u.id)
            .outerjoin(like_subquery, p2.id == like_subquery.c.id_post)
            .outerjoin(repost_subquery, p2.id == repost_subquery.c.id_post)
        )
        .where(u.is_public == True)
        .where(p2.posted_at < oldest_date)
        .order_by(desc(p2.posted_at))
        .limit(amount)
    )

    print("LO QUE DEV LA QUERIE")
    print(session.execute(query))
    return session.execute(query)



def get_public_posts_user_is_interested_in2(user_id, amount, oldest_date) :
    # Crea subconsultas para los recuentos de likes y reposts
    like_subquery = (
        session.query(
            Like.id_post,
            func.count(Like.id_post).label("like_count")
        )
        .group_by(Like.id_post)
        .subquery()
    )

    repost_subquery = (
        session.query(
            Repost.id_post,
            func.count(Repost.id_post).label("repost_count")
        )
        .group_by(Repost.id_post)
        .subquery()
    )

    # Crea aliases para las tablas
    i = aliased(Interests)
    h = aliased(Hashtag)
    p2 = aliased(Post)
    u = aliased(User)

    # Crea la consulta principal
    query = (
        select([
            Post,
            User,
            like_subquery.c.like_count,
            repost_subquery.c.repost_count
        ])
        .select_from(
            Post.__table__
            .join(i, i.user_id == user_id)
            .join(h, i.interest == h.hashtag)
            .join(p2, p2.id == h.id_post)
            .join(u, u.id == p2.user_id)
        )
        .group_by(Post.id, User.id)
        .filter(u.is_public == True)
        .filter(p2.posted_at < oldest_date)
        .order_by(desc(Post.posted_at))
        .limit(amount)
    )

    # Realiza el outerjoin con las subconsultas de likes y reposts
    query = query.outerjoin(like_subquery, like_subquery.c.id_post == Post.id)
    query = query.outerjoin(repost_subquery, repost_subquery.c.id_post == Post.id)

    # Ejecuta la consulta y obtén los resultados
    result = session.execute(query)

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

    posts = []
    if (is_following(user_id_a, user_id_b) or is_public(user_id_b)):
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