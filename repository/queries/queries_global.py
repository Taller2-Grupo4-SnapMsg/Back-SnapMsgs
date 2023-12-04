"""
Global queries and functions that could be reused in other queries
"""
from psycopg2 import IntegrityError

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.errors import *
from repository.queries.common_setup import *

# pylint: disable=C0114, W0401, W0614, E0401
from repository.tables.posts import Post

# pylint: disable=C0114, W0401, W0614, E0401
from repository.tables.users import User, Following


def get_post(post_id):
    """
    Get the post based on id
    """
    post = session.query(Post).filter(Post.post_id == post_id).first()
    if post is None:
        raise PostNotFound()

    return post


def validate_that_there_is_at_least_text_or_image(content, image):
    """
    Check that there is at least text or image
    """
    if content == "" and image == "":
        raise EmptyPostError()


def valid_content(content):
    """
    Check that both (image and content) are not null and if
    the content is longer than 1000 chars (max lenght in DB)
    """
    if len(content) > 1000:
        raise TextTooLongError()


def is_following(user_id, user_id_to_check_if_following):
    """
    Returns True if the user with the given id is following
    the user with the given id.
    """
    following = (
        session.query(Following)
        .filter(Following.user_id == user_id)
        .filter(Following.following_id == user_id_to_check_if_following)
        .first()
    )
    return following is not None


def get_content_id_from_post(post_id):
    """
    Returns the corresponding content id from that post
    """
    post = session.query(Post).filter(Post.post_id == post_id).first()
    if post is None:
        raise PostNotFound()
    return post.content_id


def get_user_id_from_email(email):
    """
    Return the id from the user with this email
    """
    user = session.query(User).filter(User.email == email).first()
    if user is None:
        raise UserNotFound()
    return user.id


def is_public(user_id):
    """
    Returns True if the user is public.
    """
    public = (
        session.query(User)
        .filter(User.id == user_id)
        # pylint: disable=C0121
        .filter(User.is_public == True)
        .first()
    )
    return public is not None


def execute_delete_query(delete_query):
    """
    Executes the delete query passed as argument
    """
    try:
        session.execute(delete_query)
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise DatabaseError from error
