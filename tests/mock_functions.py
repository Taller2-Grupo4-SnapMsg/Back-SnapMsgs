# pylint: skip-file
"""
Functions to mock backend-user behaviour.
Normally the user would have to create their account and then navigate.
Here I have funcitons that create the user with my parameters.
No checks of verifications are made.
"""

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.common_setup import *
from repository.tables.users import User, Following, Interests
from repository.tables.posts import Post, Content, Hashtag, Mention
import datetime

# -------------------- Parameters -------------------

TOKEN_FAKE = "fake_token"
AMOUNT_DEFAULT = 10

# ---------------- Parameters user 1 ----------------

USERNAME_1 = "username1"
EMAIL_1 = "user1@gmail.com"

# ---------------- Parameters user 2 ----------------

USERNAME_2 = "username2"
EMAIL_2 = "user2@gmail.com"

# ---------------- Generic parameters users ----------------

SURNAME = "surname"
NAME = "name"
BIO = "This is a bio"
PASSWORD = "1234"
LOCATION = "Location"
AVATAR = "path_to_avatar"
DATE_OF_BIRTH = datetime.datetime(1990, 1, 1)

# ---------------- default parameters posts ----------------

TEXT = "This is a post"
IMAGE = ""
HASHTAGS = []
MENTIONS = []
USER_POSTER_ID = 1
USER_CREATOR_ID = 1

# ----------------------- others ---------------------------

LONG_TEXT = "a" * 1001

# ------------------ Save from bdd ------------------


def create_user(username=USERNAME_1, email=EMAIL_1, is_public=True, is_blocked=False):
    """
    Creates a user with the given parameters
    """
    new_user = User(
        username=username,
        email=email,
        is_public=is_public,
        blocked=is_blocked,
        surname=SURNAME,
        name=NAME,
        password=PASSWORD,
        date_of_birth=DATE_OF_BIRTH,
        bio=BIO,
        avatar=AVATAR,
        location=LOCATION,
    )
    session.add(new_user)
    session.commit()
    return new_user


def create_post(
    user_id,
    content=TEXT,
    image=IMAGE,
    hashtags=HASHTAGS,
    mentions=MENTIONS,
):
    """
    Creates a post with the given parameters

    - content: text of the post
    - image: path to image of the post
    - hashtags: list of hashtags
    - mentions: list of user ids
    - user_poster_id: id of the user that posted the post
    - user_creator_id: id of the user that created the post
    """

    new_content = Content(
        text=content,
        image=image,
    )
    session.add(new_content)

    session.commit()

    for hashtag in hashtags:
        new_hashtag = Hashtag(
            content_id=new_content.content_id,
            hashtag=hashtag,
        )
        session.add(new_hashtag)

    for user_mention_id in mentions:
        new_mention = Mention(
            content_id=new_content.content_id,
            user_mention_id=user_mention_id,
        )
        session.add(new_mention)

    new_post = Post(
        user_poster_id=user_id,
        user_creator_id=user_id,
        content_id=new_content.content_id,
    )
    session.add(new_post)

    session.commit()

    return new_post


def create_repost(user_poster_id, user_creator_id, content_id):
    """
    Creates a repost with the given parameters

    - user_poster_id: id of the user that posted the post
    - user_creator_id: id of the user that created the post
    - content_id: id of the content that is being reposted
    """

    new_post = Post(
        user_poster_id=user_poster_id,
        user_creator_id=user_creator_id,
        content_id=content_id,
    )
    session.add(new_post)

    session.commit()

    return new_post


def create_follow(user_id, following_id):
    new_follow = Following(
        user_id=user_id,
        following_id=following_id,
    )

    session.add(new_follow)
    session.commit()

    return new_follow


def create_interest(user_id, interest):
    new_interest = Interests(
        user_id=user_id,
        interest=interest,
    )

    session.add(new_interest)
    session.commit()

    return new_interest


# ------------------ Delete from bdd ------------------


def user_delete(user):
    session.delete(user)
    session.commit()


def delete_content_by_content_id(content_id: int):
    content_to_delete = (
        session.query(Content).filter(Content.content_id == content_id).first()
    )

    if content_to_delete:
        session.delete(content_to_delete)
        session.commit()
        return True
    else:
        return False


def delete_hashtags_by_content_id(content_id: int):
    hashtags_to_delete = (
        session.query(Hashtag).filter(Hashtag.content_id == content_id).all()
    )

    for hashtag in hashtags_to_delete:
        if hashtag:
            session.delete(hashtag)
            session.commit()
            return True
        else:
            return False


def delete_posts_by_content_id(content_id: int):
    posts_to_delete = session.query(Post).filter(Post.content_id == content_id).all()

    for post in posts_to_delete:
        if post:
            session.delete(post)
            session.commit()
            return True
        else:
            return False


def delete_mentions_by_content_id(content_id: int):
    mentions_to_delete = (
        session.query(Mention).filter(Mention.content_id == content_id).all()
    )

    for mention in mentions_to_delete:
        if mention:
            session.delete(mention)
            session.commit()
            return True
        else:
            return False


def post_delete(post):
    if post.user_creator_id == post.user_poster_id:
        delete_mentions_by_content_id(post.content_id)
        delete_hashtags_by_content_id(post.content_id)
        delete_posts_by_content_id(post.content_id)
        delete_content_by_content_id(post.content_id)
    else:
        delete_posts_by_content_id(post.content_id)


def post_delete_by_id(post_id: int):
    post_to_delete = session.query(Post).filter(Post.post_id == post_id).first()

    if post_to_delete:
        post_delete(post_to_delete)
        return True
    else:
        return False


def delete_all_posts():
    posts_to_delete = session.query(Post).all()

    for post in posts_to_delete:
        post_delete(post)


def delete_follow(user_id: int, following_id: int):
    follow_to_delete = (
        session.query(Following)
        .filter(Following.user_id == user_id)
        .filter(Following.following_id == following_id)
        .first()
    )

    if follow_to_delete:
        session.delete(follow_to_delete)
        session.commit()
        return True
    else:
        return False


# ---------- Solo debug ----------


def delete_user_by_username(username: str):
    user_to_delete = session.query(User).filter(User.username == username).first()

    if user_to_delete:
        session.delete(user_to_delete)
        session.commit()
        return True
    else:
        return False
