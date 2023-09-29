# We connect to the database using the ORM defined in tables.py
from operator import and_
import os
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker

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

# id = Column(Integer, primary_key=True)
# user_id = Column(Integer, nullable=False)
# user = relationship(UserRemote, backref='posts')

# posted_at = Column(DateTime, default=datetime.datetime.utcnow)
# content = Column(String(800), unique=False, nullable=True)
# image = Column(String(100), unique=False, nullable=True)


def create_post(user_id, posted_at, content, image):
    """ """
    post = Posts(
        user_id=user_id,
        posted_at=posted_at,
        content=content,
        image=image,
    )

    session.add(post)
    session.commit()
    return post


def create_like(id_post, user_id):
    """ """
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

# get de todos los likes para debbuguimg
# get de todos los likes que cierto usuario realizó
# get de todos los likes que cierto post tuvo


# ---------Remove----------


def remove_like(like_id):
    """
    Removes the folowing relation between the two users.
    """
    like = session.query(Likes).filter(Likes.like_id == like_id).first()
    if like:
        session.delete(like)
        session.commit()
        return
    raise KeyError("The relation doesn't exist")


def remove_post(id_post):
    """
    Removes the folowing relation between the two users.
    """
    post = session.query(Posts).filter(Posts.id == id_post).first()
    if post:
        session.delete(post)
        session.commit()
        return
    raise KeyError("The relation doesn't exist")

def remove_posts():
    """
    Removes all posts.
    """
    session.query(Posts).delete()
    session.commit()

