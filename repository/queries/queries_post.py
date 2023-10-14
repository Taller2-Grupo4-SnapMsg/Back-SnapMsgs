"""
Archivo con algunas pruebas de la base de datos
"""
from typing import List
from sqlalchemy import and_, exists, or_, func
from sqlalchemy import desc
from sqlalchemy.orm import aliased
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.common_setup import *

# pylint: disable=C0114, W0401, W0614, E0401
from repository.errors import (
    PostNotFound,
    UserNotFound,
    NegativeOrZeroAmount,
    DatabaseError,
)

# pylint: disable=C0114, W0401, W0614, E0401
from repository.tables.posts import Post, Like, Repost, Hashtag

# pylint: disable=C0114, W0401, W0614, E0401
from repository.tables.users import User, Following


# ----- CREATE ------

def create_hashtag(id_post: int, hashtags: List[str]):
    print("ENTRA A CREAR HASTTAG")
    print(hashtags)
    try:
        for hashtag in hashtags:
            new_hashtag = Hashtag(id_post=id_post, 
                                  hashtag=hashtag)
            session.add(new_hashtag)
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise DatabaseError from error
    return


def create_post(user_id, content, image):
    """
    Create a post made by the user_id, with that content and image
    """
    post = Post(
        user_id=user_id,
        content=content,
        image=image,
    )

    try:
        session.add(post)
        session.commit()
        return post
    except IntegrityError as error:
        session.rollback()
        raise DatabaseError from error


# ------------- GET ----------------


# listo
def get_post_by_id2(post_id):
    """
    Searches the specific post based on id

    The return value is a Post.
    """
    post = session.query(Post, User).filter(Post.id == post_id).join(User).first()
    if not post:
        raise PostNotFound
    return post


# listo
def get_posts_by_user_id(user_id):
    """
    Searches all posts from that user

    The return value is a list of Posts.
    The posts are ordered from newest to oldest
    """
    posts = (
        session.query(Post, User)
        .join(Post)
        .filter(Post.user_id == user_id)
        .order_by(Post.posted_at.desc())
    )
    if not posts:
        raise UserNotFound
    return posts


def get_posts_by_user_and_date(user_id, date):
    """
    Searches for posts made by the user on the specific date

    The return value is a list of Posts
    The posts are ordered from newest to oldest
    """
    return (
        session.query(Post)
        .filter(and_(Post.user_id == user_id, Post.posted_at == date))
        .order_by(desc(Post.posted_at))
        .all()
    )


def get_posts_by_user_between_dates(user_id, start_date, end_date):
    """
    Searches the posts made by the user on a specific time frame

    The return value is a list of Posts.
    The posts are ordered from newest to oldest
    """
    return (
        session.query(Post)
        .filter(
            and_(Post.user_id == user_id, Post.posted_at.between(start_date, end_date))
        )
        .order_by(desc(Post.posted_at))
        .all()
    )


# listo
def get_newest_post_by_user(user_id):
    """
    Searches the newest post made by that user

    The return value is a Post.
    """
    post = (
        session.query(Post)
        .filter(Post.user_id == user_id)
        .order_by(desc(Post.posted_at))
        .first()
    )
    if not post:
        raise PostNotFound
    return post


# listo
def get_x_newest_posts_by_user(user_id, amount):
    """
    Searches the x amount of newest posts made by that user

    The return value is a list of Post.
    """
    if amount <= 0:
        raise NegativeOrZeroAmount

    posts = (
        session.query(Post)
        .filter(Post.user_id == user_id)
        .order_by(desc(Post.posted_at))
        .limit(amount)
        .all()
    )
    if not posts:
        raise UserNotFound
    return posts


def get_x_newest_posts(amount):
    """
    Retrieves all posts in db with all the corresponding user info.

    Raises:
        PostNotFound: If a post is not found.
    """

    if amount <= 0:
        raise NegativeOrZeroAmount

    results = (
        session.query(Post, User)
        .join(User, Post.user_id == User.id)
        .order_by(desc(Post.posted_at))
        .limit(amount)
        .all()
    )

    if not results:
        raise PostNotFound()

    return results

#-----------new queries----------------






#aca despues va a tener que contemplar que solo me muestre los publicos que 
#van con mis intereses
def get_visible_posts(user_id):
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

    # Consulta para obtener los posts visibles para el usuario
    visible_posts = (
        session.query(
            Post,
            likes_subquery,
            reposts_subquery
        )
        .join(User, User.id == Post.user_id)
        .outerjoin(Following, and_(Following.user_id == user_id, Following.following_id == Post.user_id))
        .filter(
            or_(
                and_(Following.user_id == user_id, Following.following_id == user_id),
                Post.is_public == True,
            )
        )
        .group_by(Post.id)
        .order_by(Post.posted_at.desc())
        .all()
    )

    return visible_posts


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

    # Consulta para obtener los posts visibles para el usuario A cuando visita el perfil del usuario B
    visible_posts = (
        session.query(
            Post,
            likes_subquery,
            reposts_subquery
        )
        .join(User, Post.user_id == user_b_id)
        .outerjoin(Following, Following.user_id == user_a_id)
        .outerjoin(Like, Like.id_post == Post.id)
        .outerjoin(Repost, Repost.id_post == Post.id)
        .filter(
            (
                (user_a_id == user_b_id)  # Si el usuario A visita su propio perfil
                | Following.following_id == user_b_id  # Usuario A sigue a B
                | (Post.is_public == True)  # El post es público
            )
        )
        .group_by(Post.id)
        .order_by(Post.posted_at.desc())
        .all()
    )

    return visible_posts


# --------- Put ----------

def put_post(modified_post):
    """
    Searches the post with the same id and updates it
    The function updates all the info from the post in the db
    with the info in the modified_post.
    Be sure everything that is allowed to be modified
    is in the modified_post!
    That is content, image and etiquetas

    Raises PostNotFound if not foun
    """
    existing_post = session.query(Post).filter(Post.id == modified_post.id).first()
    if not existing_post:
        raise PostNotFound

    #Update what we allow to be updated
    existing_post.content = modified_post.content
    existing_post.image = modified_post.image
    #falta modificar las etiquetas de las publicaciones
    
    session.commit()


# --------- Delete ----------


def delete_post(id_post):
    """
    Deletes the folowing relation between the two users.
    """
    post = session.query(Post).filter(Post.id == id_post).first()
    if post:
        session.delete(post)
        session.commit()
        return
    raise UserNotFound()


def delete_posts_by_user(user_id):
    """
    Deletes the posts made by that user
    """
    post = session.query(Post).filter(Post.user_id == user_id).all()
    if post:
        session.delete(post)
        session.commit()
        return
    raise UserNotFound()


def delete_posts():
    """
    Deletes all posts.
    """
    session.query(Post).delete()
    session.commit()


def get_posts():
    """
    Retrieves all posts in db with all the corresponding user info.



    Raises:
        PostNotFound: If a post is not found.
    """

    results = (
        session.query(Post, User)
        .join(User, Post.user_id == User.id)
        .order_by(desc(Post.posted_at))
        .all()
    )

    if not results:
        raise PostNotFound()

    return results


#----------------No va - Pero está en los tests----------------

# para que no falle coverange, pero creo que no va
def get_post_by_id(post_id):
    """
    Searches the specific post based on id

    The return value is a Post.
    """
    post = session.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise PostNotFound
    return post

