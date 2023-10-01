"""
This is the test module.
"""
import pytest

# pylint: disable=C0114, W0401, W0614
from repository.queries.queries import *

# pylint: disable=C0114, W0401, W0614
from repository.errors import *

NON_EXISTANT_USER_ID = -2

USER_ID = -1
CONTENT1 = "the incredibly original content -- fisrt content"
IMAGE1 = "a new image -- first image"

CONTENT2 = "the incredibly original content -- second content"
IMAGE2 = "a new image -- second image"


def delete_test_posts_from_db(id_post: int):
    """
    This function removes the test user from the database.
    """
    try:
        delete_post(id_post)
    except UserNotFound:
        return


def create_test_post_from_db():
    """
    This function creates and saves the test post to the database
    Returns the newly created post
    """
    post1 = create_post(USER_ID, CONTENT1, IMAGE1)
    post2 = create_post(USER_ID, CONTENT2, IMAGE2)
    return post1, post2


@pytest.fixture(scope="module")
def test_posts():
    """
    Fixture to create and save a test post to the database
    """
    post1, post2 = create_test_post_from_db()
    yield post1, post2  # This allows the test to run
    # Teardown: Remove the test post after the tests
    delete_test_posts_from_db(post1.id)
    delete_test_posts_from_db(post2.id)


# pylint: disable=W0621
def test_get_post_by_id(test_posts):
    """
    Test function for get_post_by_id
    """
    post1, post2 = test_posts
    assert get_post_by_id(post1.id) == post1
    assert get_post_by_id(post2.id) == post2


# pylint: disable=W0621
def test_get_posts_by_user_id(test_posts):
    """
    Test function for get_post_by_id
    """
    post1, post2 = test_posts
    retrieved_posts = get_posts_by_user_id(USER_ID)
    assert retrieved_posts
    assert len(retrieved_posts) == 2
    assert retrieved_posts[0] == post2  # Check the first element
    assert retrieved_posts[1] == post1  # Check the first element


def test_get_posts_by_user_id_with_invalid_id_raises_exception():
    """
    Test function for get_post_by_id
    """
    with pytest.raises(UserNotFound):
        get_posts_by_user_id(NON_EXISTANT_USER_ID)
