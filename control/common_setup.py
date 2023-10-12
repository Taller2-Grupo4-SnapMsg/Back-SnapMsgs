"""
Clases for the response bodies of the posts and likes controller.
There are also functions to generate the correct classes from the db objects
and from the json objects.
"""

from pydantic import BaseModel

POST_NOT_FOUND = 404
USER_NOT_FOUND = 404
LIKE_NOT_FOUND = 404
BAD_REQUEST = 400

API_BASE_URL = "https://loginback-lg51.onrender.com"

# ------------------------------------------ POSTS ------------------------------------------


# Define a Pydantic model for the request body
class PostCreateRequest(BaseModel):
    """
    This class is a Pydantic model for the request body.
    """

    content: str
    image: str


class UserResponse(BaseModel):
    """
    This class is a Pydantic model for the User part of the response body.
    This way, with the post in the response, the front already gets the information from
    the corresponding User
    """

    username: str
    name: str
    last_name: str
    avatar: str


class PostResponse(BaseModel):
    """
    This class is a Pydantic model for the response body.
    """

    id: int
    user: UserResponse
    posted_at: str
    content: str
    image: str
    amount_likes: int
    amount_reposts: int
    

    # I disable it since it's a pydantic configuration
    # pylint: disable=too-few-public-methods
    class Config:
        """
        This is a pydantic configuration so I can cast
        orm_objects into pydantic models.
        """

        orm_mode = True
        from_attributes = True


class PostToEdit(BaseModel):
    """
    This class is a Pydantic model for the response body.
    """

    id: int
    content: str
    image: str

    # I disable it since it's a pydantic configuration
    # pylint: disable=too-few-public-methods
    class Config:
        """
        This is a pydantic configuration so I can cast
        orm_objects into pydantic models.
        """

        orm_mode = True
        from_attributes = True



def generate_user_from_db(user):
    """
    This function casts the orm_object into a pydantic model.
    (from data base object to json)
    """
    return UserResponse(
        username=user.username,
        name=user.name,
        last_name=user.surname,
        avatar=user.avatar,
    )


def generate_post_from_db(post, user):
    """
    This function casts the orm_object into a pydantic model.
    (from data base object to json)
    """
    return PostResponse(
        id=post.id,
        user=generate_user_from_db(user),
        posted_at=str(post.posted_at),
        content=post.content,
        image=post.image,
    )


# pylint: disable=C0116
def generate_response_posts_with_users_from_db(posts_and_users):
    response = []
    for pair in posts_and_users:
        response.append(generate_post_from_db(pair[0], pair[1]))
    return response


def generate_user_from_back_user(user):
    """
    This function casts the orm_object into a pydantic model.
    (from data base object to json)
    """
    return UserResponse(
        username=user.get("username"),
        name=user.get("name"),
        last_name=user.get("last_name"),
        avatar=user.get("avatar"),
    )


def generate_post_from_back_user(post, user):
    """
    This function casts the orm_object into a pydantic model.
    (from data base object to json)
    """
    return PostResponse(
        id=post.id,
        user=generate_user_from_back_user(user),
        posted_at=str(post.posted_at),
        content=post.content,
        image=post.image,
    )


# pylint: disable=C0116
def generate_response_posts_with_user_from_back_user(posts, user):
    response = []
    for post in posts:
        response.append(generate_post_from_back_user(post, user))
    return response


def generate_response_users_with_user_from_back_user(users):
    response = []
    for user in users:
        response.append(generate_user_from_db(user))
    return response


# ------------------------------------------ LIKES ------------------------------------------


# Define a Pydantic model for the request body
class LikeCreateRequest(BaseModel):
    """
    This class is a Pydantic model for the request body.
    """

    post_id: int

    # I disable it since it's a pydantic configuration
    # pylint: disable=too-few-public-methods
    class Config:
        """
        This is a pydantic configuration so I can cast
        orm_objects into pydantic models.
        """

        orm_mode = True
        from_attributes = True
