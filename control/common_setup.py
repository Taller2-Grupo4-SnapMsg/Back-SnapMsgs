"""
Clases for the response bodies of the posts and likes controller.
There are also functions to generate the correct classes from the db objects
and from the json objects.
"""
from typing import List
from fastapi import HTTPException
from pydantic import BaseModel
import httpx

POST_NOT_FOUND = 404
USER_NOT_FOUND = 404
LIKE_NOT_FOUND = 404
BAD_REQUEST = 400

API_BASE_URL = "https://gateway-api-merok23.cloud.okteto.net"


# ------------------------------------------ POSTS ------------------------------------------


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
    name: str
    is_public: bool


class PostResponse(BaseModel):
    """
    This class is a Pydantic model for the response body.
    """

    post_id: int
    user_poster: UserResponse
    user_creator: UserResponse
    created_at: str
    text: str
    image: str
    number_likes: int
    number_reposts: int
    hashtags: List[str]
    did_i_like: bool
    did_i_repost: bool

    # I disable it since it's a pydantic configuration
    # pylint: disable=too-few-public-methods
    class Config:
        """
        This is a pydantic configuration so I can cast
        orm_objects into pydantic models.
        """

        orm_mode = True
        from_attributes = True


# pylint: disable=R0913
def generate_post_from_db(
    post_info, content_info, user_poster_id,
        user_poster_name,
        user_poster_is_public,
        user_creator_id,
        user_creator_name,
        user_creator_is_public, hashtags, 
    likes_count, reposts_count, did_i_like, did_i_repost,
):
    """
    This function casts the orm_object into a pydantic model.
    (from data base object to json)
    """
    return PostResponse(
        post_id=post_info.post_id,
        user_poster=generate_user_from_db(user_poster_id, user_poster_name, user_poster_is_public),
        user_creator=generate_user_from_db(user_creator_id, user_creator_name, user_creator_is_public),
        created_at=str(post_info.created_at),
        text=content_info.text,
        image=content_info.image,
        number_likes=likes_count,
        number_reposts=reposts_count,
        hashtags=hashtags,
        did_i_like=did_i_like,
        did_i_repost=did_i_repost,
    )

#listo
def generate_user_from_db(user_id,
        user_name,
        user_public):
    """
    This function casts the orm_object into a pydantic model.
    (from data base object to json)
    """
    return UserResponse(
        id=user_id,
        name=user_name,
        is_public=user_public,
    )

#listo
def generate_post(post_db):
    """
    This function casts the orm_object into a pydantic model.
    """
    (
        post_info,
        content_info,
        user_poster_id,
        user_poster_name,
        user_poster_is_public,
        user_creator_id,
        user_creator_name,
        user_creator_is_public,
        hashtags,
       likes_count,
       reposts_count,
       did_i_like,
       did_i_repost,
    ) = post_db

    if likes_count is None:
        likes_count = 0
    if reposts_count is None:
        reposts_count = 0
    if hashtags is None:
       hashtags = []

    return generate_post_from_db(
        post_info,
        content_info,
        user_poster_id,
        user_poster_name,
        user_poster_is_public,
        user_creator_id,
        user_creator_name,
        user_creator_is_public,
        hashtags,
       likes_count,
       reposts_count,
       did_i_like,
       did_i_repost,
    )

#listo
def generate_response_posts_from_db(posts_db):
    """
    This function casts the orm_object into a pydantic model.
    """
    response = []
    for post_db in posts_db:
        post = generate_post(post_db)
        response.append(post)

    return response


# ------------------------------------------ LIKES ------------------------------------------


class LikeCreateRequest(BaseModel):
    """
    This class is a Pydantic model for the request body.
    """

    content_id: int

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
    """
    This function gets the user from the token.
    """
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
