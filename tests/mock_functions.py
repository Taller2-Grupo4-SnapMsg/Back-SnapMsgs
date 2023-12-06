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
from repository.tables.posts import (
    Post,
    Content,
    Hashtag,
    Mention,
    Favorite,
    Like,
    DeviceToken,
)
import datetime

# -------------------- Parameters -------------------

TOKEN_FAKE = "fake_token"
DEVICE_TOKEN = "device_token"
AMOUNT_DEFAULT = 10
OFFSET_DEFAULT = 0
DAYS_DEFAULT = 7

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
INTEREST_1 = "interest_1"
INTEREST_2 = "interest_2"
HASHTAG_1 = "hashtag_1"
HASHTAG_2 = "hashtag_2"

# ---------------- default parameters posts ----------------

TEXT = "This is a post"
IMAGE = ""
HASHTAGS = []
MENTIONS = []
USER_POSTER_ID = 1
USER_CREATOR_ID = 1

# ---------------- notification data request ---------------

TITLE = "title"
BODY = "body"
DATA = {}

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

    return [new_post, new_content.content_id]


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


def create_favorite(user_id, content_id):
    new_favorite = Favorite(
        user_id=user_id,
        content_id=content_id,
    )

    session.add(new_favorite)
    session.commit()

    return new_favorite


def create_like(user_id, content_id):
    new_like = Like(
        user_id=user_id,
        content_id=content_id,
    )

    session.add(new_like)
    session.commit()

    return new_like


def save_device_token(user_id, token):
    new_token = DeviceToken(
        user_id=user_id,
        device_token=token,
    )

    session.add(new_token)
    session.commit()

    return new_token


# ------------------ Delete from bdd ------------------


def delete_all_posts():
    posts_to_delete = session.query(Post).all()

    for post in posts_to_delete:
        session.delete(post)
        session.commit()


def delete_all_contents():
    contents_to_delete = session.query(Content).all()

    for content in contents_to_delete:
        session.delete(content)
        session.commit()


def delete_all_favorites():
    favorites_to_delete = session.query(Favorite).all()

    for favorite in favorites_to_delete:
        session.delete(favorite)
        session.commit()


def delete_all_likes():
    likes_to_delete = session.query(Like).all()

    for like in likes_to_delete:
        session.delete(like)
        session.commit()


def delete_all_follows():
    follows_to_delete = session.query(Following).all()

    for follow in follows_to_delete:
        session.delete(follow)
        session.commit()


def delete_all_users():
    users_to_delete = session.query(User).all()

    for user in users_to_delete:
        session.delete(user)
        session.commit()


def delete_all_device_tokens():
    device_tokens_to_delete = session.query(DeviceToken).all()

    for device_token in device_tokens_to_delete:
        session.delete(device_token)
        session.commit()


def delete_all_interests():
    interests_to_delete = session.query(Interests).all()

    for interest in interests_to_delete:
        session.delete(interest)
        session.commit()


def delete_all_hashtags():
    hashtags_to_delete = session.query(Hashtag).all()

    for hashtag in hashtags_to_delete:
        session.delete(hashtag)
        session.commit()


def delete_all_mentions():
    mentions_to_delete = session.query(Mention).all()

    for mention in mentions_to_delete:
        session.delete(mention)
        session.commit()


def delete_all():
    delete_all_favorites()
    delete_all_likes()
    delete_all_mentions()
    delete_all_hashtags()
    delete_all_posts()
    delete_all_contents()
    delete_all_follows()
    delete_all_device_tokens()
    delete_all_interests()
    delete_all_users()
