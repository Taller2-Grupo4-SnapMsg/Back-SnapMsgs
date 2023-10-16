# pylint: skip-file
"""
This is the test module.
"""
import pytest

# pylint: disable=C0114, W0401, W0614, E0401, E0602, C0116
from repository.queries.queries_like import *

USER_ID1 = 2
USER_ID2 = 60

POST_ID1 = 1
POST_ID2 = 2


# def create_like(id_post, user_id)
# def get_likes_from_post(post_id)
# def get_the_number_of_likes(post_id)
# def get_user_likes(user_id)
# def get_all_the_likes()
# def delete_like(user_id, post_id)
# def delete_likes()


def create_test_like_from_db():
    """
    Esta función crea los "likes" de prueba en la base de datos.
    """
    # Crea el "like" de prueba para POST_ID1 aquí
    like1 = create_like(POST_ID1, USER_ID1)
    like2 = create_like(POST_ID2, USER_ID2)
    return like1, like2


def delete_test_likes_from_db(user_id: int, id_post: int):
    """
    This function removes the test user from the database.
    """
    try:
        delete_like(user_id, id_post)
    except UserNotFound:
        return


# ...


@pytest.fixture(scope="module")
def test_likes_db():
    """
    Fixture para los "likes" de prueba.
    """
    like1, like2 = create_test_like_from_db()
    yield like1, like2
    delete_test_likes_from_db(USER_ID1, POST_ID1)
    delete_test_likes_from_db(USER_ID2, POST_ID2)


# ...


def test_get_like_for_a_post(test_likes):
    """
    Función de prueba para get_like_for_a_post
    """
    like1, _ = test_likes
    users_liked = get_likes_from_post(like1.id_post)
    print(f"USERS_LIKED: {users_liked}")
    assert users_liked and (USER_ID1 in users_liked)
