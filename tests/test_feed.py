# pylint: skip-file
"""
This is the test module.
"""
import datetime
import pytest

# pylint: disable=C0114, W0401, W0614, E0401, E0602, C0116
from repository.queries.V_queries_global import *
from repository.queries.V_queries_post import *
from tests.mock_functions import *
from repository.tables.posts import Post


@pytest.fixture(autouse=True)
def clear_tables():
    session.query(User).delete()
    session.query(Interests).delete()
    session.query(Following).delete()
    session.query(Post).delete()
    session.query(Hashtag).delete()
    session.commit()


# ---------------- GET but nothing is returned ----------------


def test_user_doesnt_follow_anybody_nor_does_he_have_interests():
    user = user_save(
        "BellaIsMissing", "Goth", "Bella", "12345", "bella@gmail.com", True
    )
    posts = get_post_for_user_feed(user.id, 10, datetime.datetime.now())
    assert len(posts) == 0, "The list is not empty"


def test_user_follows_user_without_posts_and_doesnt_have_interests():
    user_follower = user_save(
        "MortimerIsLooking", "Goth", "Mortimer", "2468", "morti@gmail.com", True
    )
    user_followed = user_save(
        "BellaIsMissing", "Goth", "Bella", "12345", "bella@gmail.com", True
    )
    follow_save(user_follower.id, user_followed.id)

    posts = get_post_for_user_feed(user_follower.id, 10, datetime.datetime.now())
    assert len(posts) == 0, "The list is not empty"


def test_user_doesnt_follow_and_has_interests_that_no_post_matches():
    user = user_save(
        "BellaIsMissing", "Goth", "Bella", "12345", "bella@gmail.com", True
    )
    interest_save(user.id, "Red")
    interest_save(user.id, "Aliens")

    posts = get_post_for_user_feed(user.id, 10, datetime.datetime.now())
    assert len(posts) == 0, "The list is not empty"


def test_user_doesnt_follow_and_has_interests_that_match_post_but_poster_is_private():
    user = user_save(
        "MortimerIsLooking", "Goth", "Mortimer", "2468", "morti@gmail.com", True
    )
    interest_save(user.id, "Red")
    interest_save(user.id, "Aliens")

    user_poster = user_save(
        "BellaIsMissing", "Goth", "Bella", "12345", "bella@gmail.com", False
    )

    create_post(
        user_poster.id,
        "the content made by Bella about red and aliens",
        "the image link",
        ["Red", "Aliens"],
    )
    posts = get_post_for_user_feed(user.id, 10, datetime.datetime.now())
    assert len(posts) == 0, "The list is not empty"


# ---------------- GET that return because following matches ----------------


def test_user_doesnt_follow_but_has_interest_and_public_user_posts_with_those_interests():
    user = user_save(
        "MortimerIsLooking", "Goth", "Mortimer", "2468", "morti@gmail.com", True
    )
    interest_save(user.id, "Red")
    interest_save(user.id, "Aliens")

    user_poster = user_save(
        "BellaIsMissing", "Goth", "Bella", "12345", "bella@gmail.com", True
    )
    post = create_post(
        user_poster.id,
        "the content made by Bella about red and aliens",
        "the image link",
        ["Red", "Aliens"],
    )

    posts = get_post_for_user_feed(
        user.id, 10, post.posted_at + datetime.timedelta(days=1)
    )
    assert (
        len(posts) == 1
    ), "The list doesnt have the correct amount of elements in it (it should be 1)"
    assert posts[0][0].id == post.id, "The post id doesnt match"
    assert posts[0][1].id == user_poster.id, "The user id of the poster doesnt match"


def test_user_follows_public_user_but_has_no_interests():
    user_follower = user_save(
        "MortimerIsLooking", "Goth", "Mortimer", "2468", "morti@gmail.com", True
    )
    user_followed = user_save(
        "BellaIsMissing", "Goth", "Bella", "12345", "bella@gmail.com", True
    )
    follow_save(user_follower.id, user_followed.id)

    post = create_post(
        user_followed.id,
        "the content made by Bella about red and aliens",
        "the image link",
        ["Red", "Aliens"],
    )

    posts = get_post_for_user_feed(
        user_follower.id, 10, post.posted_at + datetime.timedelta(days=1)
    )
    assert (
        len(posts) == 1
    ), "The list doesnt have the correct amount of elements in it (it should be 1)"
    assert posts[0][0].id == post.id, "The post id doesnt match"
    assert posts[0][1].id == user_followed.id, "The user id of the poster doesnt match"
    assert (
        posts[0][1].id != user_follower.id
    ), "The user id of the poster is the user_follower.id"


def test_user_follows_private_user_but_has_no_interests():
    user_follower = user_save(
        "MortimerIsLooking", "Goth", "Mortimer", "2468", "morti@gmail.com", True
    )
    user_followed = user_save(
        "BellaIsMissing", "Goth", "Bella", "12345", "bella@gmail.com", False
    )
    follow_save(user_follower.id, user_followed.id)

    post = create_post(
        user_followed.id,
        "the content made by Bella about red and aliens",
        "the image link",
        ["Red", "Aliens"],
    )

    posts = get_post_for_user_feed(
        user_follower.id, 10, post.posted_at + datetime.timedelta(days=1)
    )
    assert (
        len(posts) == 1
    ), "The list doesnt have the correct amount of elements in it (it should be 1)"
    assert posts[0][0].id == post.id, "The post id doesnt match"
    assert posts[0][1].id == user_followed.id, "The user id of the poster doesnt match"
    assert (
        posts[0][1].id != user_follower.id
    ), "The user id of the poster is the user_follower.id"


def test_user_follows_public_user_and_has_interests_that_match():
    user_follower = user_save(
        "MortimerIsLooking", "Goth", "Mortimer", "2468", "morti@gmail.com", True
    )
    user_followed = user_save(
        "BellaIsMissing", "Goth", "Bella", "12345", "bella@gmail.com", True
    )
    interest_save(user_follower.id, "Red")
    interest_save(user_follower.id, "Aliens")

    follow_save(user_follower.id, user_followed.id)

    post = create_post(
        user_followed.id,
        "the content made by Bella about red and aliens",
        "the image link",
        ["Red", "Aliens"],
    )

    posts = get_post_for_user_feed(
        user_follower.id, 10, post.posted_at + datetime.timedelta(days=1)
    )
    assert (
        len(posts) == 1
    ), "The list doesnt have the correct amount of elements in it (it should be 1)"
    assert posts[0][0].id == post.id, "The post id doesnt match"
    assert posts[0][1].id == user_followed.id, "The user id of the poster doesnt match"
    assert (
        posts[0][1].id != user_follower.id
    ), "The user id of the poster is the user_follower.id"


def test_user_follows_public_user_but_has_no_interests_that_match():
    user_follower = user_save(
        "MortimerIsLooking", "Goth", "Mortimer", "2468", "morti@gmail.com", True
    )
    user_followed = user_save(
        "BellaIsMissing", "Goth", "Bella", "12345", "bella@gmail.com", True
    )
    interest_save(user_follower.id, "NotRed")
    interest_save(user_follower.id, "NotAliens")

    follow_save(user_follower.id, user_followed.id)

    post = create_post(
        user_followed.id,
        "the content made by Bella about red and aliens",
        "the image link",
        ["Red", "Aliens"],
    )

    posts = get_post_for_user_feed(
        user_follower.id, 10, post.posted_at + datetime.timedelta(days=1)
    )
    assert (
        len(posts) == 1
    ), "The list doesnt have the correct amount of elements in it (it should be 1)"
    assert posts[0][0].id == post.id, "The post id doesnt match"
    assert posts[0][1].id == user_followed.id, "The user id of the poster doesnt match"
    assert (
        posts[0][1].id != user_follower.id
    ), "The user id of the poster is the user_follower.id"


def test_user_follows_private_user_and_has_interests_that_match():
    user_follower = user_save(
        "MortimerIsLooking", "Goth", "Mortimer", "2468", "morti@gmail.com", True
    )
    user_followed = user_save(
        "BellaIsMissing", "Goth", "Bella", "12345", "bella@gmail.com", False
    )
    interest_save(user_follower.id, "Red")
    interest_save(user_follower.id, "Aliens")

    follow_save(user_follower.id, user_followed.id)

    post = create_post(
        user_followed.id,
        "the content made by Bella about red and aliens",
        "the image link",
        ["Red", "Aliens"],
    )

    posts = get_post_for_user_feed(
        user_follower.id, 10, post.posted_at + datetime.timedelta(days=1)
    )
    assert (
        len(posts) == 1
    ), "The list doesnt have the correct amount of elements in it (it should be 1)"
    assert posts[0][0].id == post.id, "The post id doesnt match"
    assert posts[0][1].id == user_followed.id, "The user id of the poster doesnt match"
    assert (
        posts[0][1].id != user_follower.id
    ), "The user id of the poster is the user_follower.id"


def test_user_follows_private_user_but_has_no_interests_that_match():
    user_follower = user_save(
        "MortimerIsLooking", "Goth", "Mortimer", "2468", "morti@gmail.com", True
    )
    user_followed = user_save(
        "BellaIsMissing", "Goth", "Bella", "12345", "bella@gmail.com", False
    )
    interest_save(user_follower.id, "NotRed")
    interest_save(user_follower.id, "NotAliens")

    follow_save(user_follower.id, user_followed.id)

    post = create_post(
        user_followed.id,
        "the content made by Bella about red and aliens",
        "the image link",
        ["Red", "Aliens"],
    )

    posts = get_post_for_user_feed(
        user_follower.id, 10, post.posted_at + datetime.timedelta(days=1)
    )
    assert (
        len(posts) == 1
    ), "The list doesnt have the correct amount of elements in it (it should be 1)"
    assert posts[0][0].id == post.id, "The post id doesnt match"
    assert posts[0][1].id == user_followed.id, "The user id of the poster doesnt match"
    assert (
        posts[0][1].id != user_follower.id
    ), "The user id of the poster is the user_follower.id"


# ---------------- GET that return because interests match ----------------
