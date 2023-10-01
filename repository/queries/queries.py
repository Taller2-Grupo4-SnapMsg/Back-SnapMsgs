# We connect to the database using the ORM defined in tables.py
from operator import and_
import os
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from repository.errors import *

from repository.tables.tables import LocalBase, Posts, Likes

# Creating engines
engine_posts = create_engine(os.environ.get("DB_URI"))

# Creating the tables in the database
LocalBase.metadata.create_all(engine_posts)

# Session is the handle of the database
Session = sessionmaker(bind=engine_posts)
session = Session()
TIMEOUT = 60

# ----- CREATE ------

def create_post(user_id, content, image):
    """ 
    Create a post made by the user_id, with that content and image
    """
    post = Posts(
        user_id=user_id,
        content=content,
        image=image,
    )

    session.add(post)
    session.commit()
    return post


def create_like(id_post, user_id):
    """ """
    print("entra a pegarle a la bdd")
    like = Likes(id_post, user_id)
    session.add(like)
    session.commit()

# ------------- GET ----------------


# --  Posts --
def get_posts():
    """
    Returns all posts, no filter

    The return value is a list of Posts.
    The posts are ordered from newest to oldest
    """
    return session.query(Posts).order_by(desc(Posts.posted_at)).all()


def get_post_by_id(post_id):
    """
    Searches the specific post based on id

    The return value is a Post.
    """
    return session.query(Posts).filter(Posts.id == post_id).first()


def get_posts_by_user_id(user_id):
    """
    Searches all posts from that user

    The return value is a list of Posts.
    The posts are ordered from newest to oldest
    """
    return (
        session.query(Posts)
        .filter(Posts.user_id == user_id)
        .order_by(desc(Posts.posted_at))
        .all()
    )


def get_posts_by_user_and_date(user_id, date):
    """
    Searches for posts made by the user on the specific date

    The return value is a list of Posts
    The posts are ordered from newest to oldest
    """
    return (
        session.query(Posts)
        .filter(and_(Posts.user_id == user_id, Posts.posted_at == date))
        .order_by(desc(Posts.posted_at))
        .all()
    )


def get_posts_by_user_between_dates(user_id, start_date, end_date):
    """
    Searches the posts made by the user on a specific time frame

    The return value is a list of Posts.
    The posts are ordered from newest to oldest
    """
    return (
        session.query(Posts)
        .filter(
            and_(
                Posts.user_id == user_id, Posts.posted_at.between(start_date, end_date)
            )
        )
        .order_by(desc(Posts.posted_at))
        .all()
    )


def get_newest_post_by_user(user_id):
    """
    Searches the newest post made by that user

    The return value is a Post.
    """
    return (
        session.query(Posts)
        .filter(Posts.user_id == user_id)
        .order_by(desc(Posts.posted_at))
        .first()
    )


def get_x_newest_posts_by_user(user_id, amount):
    """
    Searches the x amount of newest posts made by that user

    The return value is a list of Posts.
    """
    return (
        session.query(Posts)
        .filter(Posts.user_id == user_id)
        .order_by(desc(Posts.posted_at))
        .limit(amount)
        .all()
    )


def get_x_newest_posts(amount):
    """
    Searches the x amount of newest posts made by that user

    The return value is a list of Posts.
    """
    return session.query(Posts).order_by(desc(Posts.posted_at)).limit(amount).all()


# --  Likes --

def get_likes_for_a_post(post_id):
    """
    Retrieve all the likes for a specific post.

    If the post does not exist, raises a PostNotFound exception.
    """
    post = session.query(Posts).filter(Posts.id == post_id).first()
    if not post:
        raise PostNotFound()
    
    likes = session.query(Likes).filter(Likes.id_post == post_id).all()
    return likes

def get_all_the_likes():
    """
    Retrieve all likes in the system.
    """
    return session.query(Likes).all()

def get_all_the_likes_of_a_user(user_id):
    """
    Retrieve all likes given by a specific user.

    If the user does not exist, raises a UserNotFound exception.
    """
    #user = session.query(Likes).filter(Likes.user_id == user_id).first()
    #if not user:
    #    raise UserNotFound()

    likes = session.query(Likes).filter(Likes.user_id == user_id).all()
    return likes

def get_likes_count(post_id):
    """
    Returns the number of likes.
    """
    post = session.query(Posts).filter(Posts.id == post_id).first()
    if not post:
        raise PostNotFound()
    return session.query(Likes).filter(Likes.id_post == post_id).count()

# ---------Remove----------


def delete_like(user_id, post_id):
    """
    Deletes the folowing relation between the two users.
    """
    like = session.query(Likes).filter(Likes.user_id == user_id and Likes.id_post == post_id).first()
    if like:
        session.delete(like)
        session.commit()
        return
    raise LikeNotFound()


def delete_post(id_post):
    """
    Deletes the folowing relation between the two users.
    """
    post = session.query(Posts).filter(Posts.id == id_post).first()
    if post:
        session.delete(post)
        session.commit()
        return
    
    raise UserNotFound()

def delete_posts_by_user(user_id):
    """
    Deletes the posts made by that user
    """
    post = session.query(Posts).filter(Posts.user_id == user_id).all()
    if post:
        session.delete(post)
        session.commit()
        return
    
    raise UserNotFound()


def delete_posts():
    """
    Deletes all posts.
    """
    session.query(Posts).delete()
    session.commit()

def delete_likes():
    """
    Deletes all likes.
    """
    session.query(Likes).delete()
    session.commit()

