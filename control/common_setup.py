"""
Clases for the response bodies of the posts and likes controller.
There are also functions to generate the correct classes from the db objects
and from the json objects.
"""
from fastapi import HTTPException
from pydantic import BaseModel
from typing import List
import httpx

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
    hashtags: List[str]


class UserResponse(BaseModel):
    """
    This class is a Pydantic model for the User part of the response body.
    This way, with the post in the response, the front already gets the information from
    the corresponding User
    """

    id: int
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
    number_likes: int
    number_reposts: int
    hashtags: List[str]
    user_repost: UserResponse

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


def generate_post_from_db(
    post, user, likes_count, reposts_count, hashtags, user_repost, is_repost
):
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
        number_likes=likes_count,
        number_reposts=reposts_count,
        hashtags=hashtags,
        user_repost=generate_user_repost_from_db(user_repost, is_repost),
    )


def generate_user_from_db(user):
    """
    This function casts the orm_object into a pydantic model.
    (from data base object to json)
    """
    return UserResponse(
        id=user.id,
        username=user.username,
        name=user.name,
        last_name=user.surname,
        avatar=user.avatar,
    )


def generate_user_repost_from_db(user, is_repost):
    """
    This function casts the orm_object into a pydantic model.
    (from data base object to json)
    """
    if is_repost == False:
        return UserResponse(
            id=-1,
            username="",
            name="",
            last_name="",
            avatar="",
        )
    return UserResponse(
        id=user.id,
        username=user.username,
        name=user.name,
        last_name=user.surname,
        avatar=user.avatar,
    )


def generate_response_posts_from_db(posts_db):
    response = []
    for post_db in posts_db:
        (
            post_info,
            user,
            user_repost,
            likes_count,
            reposts_count,
            hashtags,
            is_repost,
        ) = post_db

        if likes_count is None:
            likes_count = 0
        if reposts_count is None:
            reposts_count = 0

        post = generate_post_from_db(
            post_info,
            user,
            likes_count,
            reposts_count,
            hashtags,
            user_repost,
            is_repost,
        )
        response.append(post)

    return response


# ------------------------------------------ LIKES ------------------------------------------


class LikeCreateRequest(BaseModel):
    """
    This class is a Pydantic model for the request body.
    """

    post_id: int

    # pylint: disable=too-few-public-methods
    class Config:
        """
        This is a pydantic configuration so I can cast
        orm_objects into pydantic models.
        """

        orm_mode = True
        from_attributes = True


# ----------------- Common functions -----------------


async def get_user_from_token(token):
    headers = {
        "Content-Type": "application/json;charset=utf-8",
        "accept": "application/json",
        "token": token,
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://gateway-api-merok23.cloud.okteto.net/user", headers=headers
        )

        if response.status_code != 200:
            raise HTTPException(status_code=400, detail={"Unknown error"})

        return response.json()
