"""
This is the test module.
"""
from datetime import datetime

import pytest
from repository.queries.queries import *
from repository.errors import *

USER_ID = -1
CONTENT = "the incredibly original content"
IMAGE = "a new image"

def delete_test_posts_from_db(id: int):
    """
    This function removes the test user from the database.
    """
    try:
        delete_post(id)
    except UserNotFound:
        return

def create_test_post_from_db():
    """
    This function creates and saves the test post to the database
    Returns the newly created post
    """
    return create_post(USER_ID, CONTENT, IMAGE)

@pytest.fixture(scope='module')
def test_post():
    """
    Fixture to create and save a test post to the database
    """
    post = create_test_post_from_db()
    yield post  # This allows the test to run
    # Teardown: Remove the test post after the tests
    delete_test_posts_from_db(post.id)
  
def test_get_post_by_id(test_post):
    """
    Test function for get_post_by_id
    """

    post_id = test_post.id
    retrieved_post = get_post_by_id(post_id)
    assert retrieved_post == test_post

def test_get_posts_by_user_id(test_post):
    """
    Test function for get_post_by_id
    """

    retrieved_posts = get_posts_by_user_id(USER_ID)
    assert retrieved_posts  # Check if the list is not empty
    assert retrieved_posts[0] == test_post  # Check the first element

