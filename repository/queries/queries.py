"""
Archivo con algunas pruebas de la base de datos
"""
from operator import and_
import os
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker

# pylint: disable=C0114, W0401, W0614, E0401
from repository.errors import (
    PostNotFound,
    LikeNotFound,
    UserNotFound,
    NegativeOrZeroAmount,
)

# pylint: disable=C0114, W0401, W0614, E0401
from repository.tables.posts import Post, Like

# pylint: disable=C0114, W0401, W0614, E0401
from repository.tables.users import Base, User

# Creating engines
engine_posts = create_engine(os.environ.get("DB_URI"))

# Creating the tables in the database
Base.metadata.create_all(engine_posts)

# Session is the handle of the database
Session = sessionmaker(bind=engine_posts)
session = Session()
TIMEOUT = 60

# ----- CREATE ------


def create_post(user_id, content, image):
    """
    Create a post made by the user_id, with that content and image
    """
    post = Post(
        user_id=user_id,
        content=content,
        image=image,
    )

    session.add(post)
    session.commit()
    return post


def create_like(id_post, user_id):
    """
    Create a like
    """
    print("entra a pegarle a la bdd")
    like = Like(id_post, user_id)
    session.add(like)
    session.commit()


# ------------- GET ----------------


# --  Posts --
# def get_posts():
#     """
#     Returns all posts, no filter

#     The return value is a list of Posts.
#     The posts are ordered from newest to oldest
#     """
#     return session.query(Post).order_by(desc(Post.posted_at)).all()


# listo
def get_post_by_id(post_id):
    """
    Searches the specific post based on id

    The return value is a Post.
    """
    post = session.query(Post).filter(Post.id == post_id).first()
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
        session.query(Post)
        .filter(Post.user_id == user_id)
        .order_by(desc(Post.posted_at))
        .all()
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
    Searches the x amount of newest posts made by that user

    The return value is a list of Post.
    """
    if amount <= 0:
        raise NegativeOrZeroAmount

    return session.query(Post).order_by(desc(Post.posted_at)).limit(amount).all()


# --  Like --


def get_likes_for_a_post(post_id):
    """
    Retrieve all the likes for a specific post.

    If the post does not exist, raises a PostNotFound exception.
    """
    post = session.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise PostNotFound()
    likes = session.query(Like).filter(Like.id_post == post_id).all()
    return likes


def get_all_the_likes():
    """
    Retrieve all likes in the system.
    """
    return session.query(Like).all()


def get_all_the_likes_of_a_user(user_id):
    """
    Retrieve all likes given by a specific user.

    If the user does not exist, raises a UserNotFound exception.
    """
    # user = session.query(Like).filter(Like.user_id == user_id).first()
    # if not user:
    #    raise UserNotFound()

    likes = session.query(Like).filter(Like.user_id == user_id).all()
    return likes


def get_likes_count(post_id):
    """
    Returns the number of likes.
    """
    post = session.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise PostNotFound()
    return session.query(Like).filter(Like.id_post == post_id).count()


# ---------Remove----------


def delete_like(user_id, post_id):
    """
    Deletes the folowing relation between the two users.
    """
    like = (
        session.query(Like)
        .filter(Like.user_id == user_id and Like.id_post == post_id)
        .first()
    )
    if like:
        session.delete(like)
        session.commit()
        return
    raise LikeNotFound()


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


def delete_likes():
    """
    Deletes all likes.
    """
    session.query(Like).delete()
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


# def get_posts_by_user_id(user_id):
#     """
#     Retrieves posts of a specific user along with user information.

#     Args:
#         user_id (int): The ID of the user whose Post to retrieve.
#         n (int): Number of Post to retrieve.

#     Raises:
#         PostNotFound: If a post is not found.
#     """

#     results = (
#         session.query(Post)
#         .filter(Post.user_id == user_id)
#         .order_by(desc(Post.posted_at)).all()
#     )

#     if not results:
#         raise PostNotFound()

#     return results


# def get_recent_post_by_user(user_id, n):
#     """
#     Retrieves the n most recent Post of a specific user along with user information.

#     Args:
#         user_id (int): The ID of the user whose Post to retrieve.
#         n (int): Number of Post to retrieve.

#     Raises:
#         PostNotFound: If a post is not found.
#     """
#     results = (
#         session.query(Post, User)
#         .join(User, Post.user_id == User.id)
#         .filter(User.id == user_id)
#         .order_by(desc(Post.posted_at))
#         .limit(n)
#         .all()
#     )

#     if not results:
#         raise PostNotFound()

#     return results
