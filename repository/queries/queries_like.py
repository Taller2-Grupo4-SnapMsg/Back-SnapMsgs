# pylint: disable=R0801
"""
Archivo con algunas pruebas de la base de datos
"""
from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.common_setup import *

# pylint: disable=C0114, W0401, W0614, E0401
from repository.errors import PostNotFound, LikeNotFound, UserNotFound, DatabaseError

# pylint: disable=C0114, W0401, W0614, E0401
from repository.tables.posts import Post, Like

# pylint: disable=C0114, W0401, W0614, E0401
from repository.tables.users import User

# ----------- Post --------------


def create_like(id_post, user_id):
    """
    Create a like
    """
    try:
        like = Like(id_post, user_id)
        session.add(like)
        session.commit()
        return like
    except IntegrityError as error:
        session.rollback()
        raise DatabaseError from error


# ----------- Get --------------


def get_likes_from_post(post_id):
    """
    Retrieve all the likes for a specific post.

    If the post does not exist, raises a PostNotFound exception.
    """
    print(f"POST_ID: {post_id}")
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
    Retrieves posts liked by a specific user, with post and user information.

    Args:
        user_id (int): The ID of the user for whom to retrieve liked posts.

    Returns:
        List[Tuple[Post, User]]: A list of tuples containing Post and User objects for liked posts.

    Raises:
        UserNotFound: If the specified user is not found.
    """
    user = session.query(User).filter(User.id == user_id).first()

    if not user:
        raise UserNotFound()

    liked_posts = (
        session.query(Post, User)
        .join(Like, Post.id == Like.id_post)
        .join(User, Post.user_id == User.id)
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
