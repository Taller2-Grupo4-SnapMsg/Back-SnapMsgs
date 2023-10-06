# pylint: disable=R0801
"""
Archivo con algunas pruebas de la base de datos
"""
import os
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker

# pylint: disable=C0114, W0401, W0614, E0401
from repository.errors import (
    PostNotFound,
    LikeNotFound,
    UserNotFound,
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

# ----------- Post --------------


def create_like(id_post, user_id):
    """
    Create a like
    """
    like = Like(id_post, user_id)
    session.add(like)
    session.commit()


# ----------- Get --------------


def get_likes_from_post(post_id):
    """
    Retrieve all the likes for a specific post.

    If the post does not exist, raises a PostNotFound exception.
    """
    post = session.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise PostNotFound()

    users = (
        session.query(User)
        .join(Like, User.id == Like.user_id)
        .filter(Like.id_post == post_id)
        .all()
    )

    return users


def get_the_number_of_likes(post_id):
    """
    Returns the number of likes.
    """
    post = session.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise PostNotFound()
    return session.query(Like).filter(Like.id_post == post_id).count()


def get_user_likes(user_id):
    """
    Retrieves posts liked by a specific user, sorted by most recent.

    Args:
        user_id (int): The ID of the user for whom to retrieve liked posts.

    Returns:
        List[Post]: A list of posts liked by the user, sorted by most recent.

    Raises:
        UserNotFound: If the specified user is not found.
    """
    user = session.query(User).filter(User.id == user_id).first()

    if not user:
        raise UserNotFound()

    liked_posts = (
        session.query(Post)
        .join(Like, Post.id == Like.id_post)
        .filter(Like.user_id == user_id)
        .order_by(desc(Post.posted_at))
        .all()
    )

    return liked_posts


def get_all_the_likes():
    """
    Retrieve all likes in the system.
    """
    return session.query(Like).all()


# ----------- Delete --------------


def delete_like(user_id, post_id):
    """
    Deletes the folowing relation between the two users.
    """
    print(f"USER_ID: {user_id}")
    print(f"POST_ID: {post_id}")
    # like = session.query(Like).filter(Like.user_id == user_id, Like.post_id == post_id).first()
    like = (
        session.query(Like)
        .filter(Like.user_id == user_id, Like.id_post == post_id)
        .first()
    )
    if like:
        session.delete(like)
        session.commit()
        return
    raise LikeNotFound()


def delete_likes():
    """
    Deletes all likes.
    """
    session.query(Like).delete()
    session.commit()
