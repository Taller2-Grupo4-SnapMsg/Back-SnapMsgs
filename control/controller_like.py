# pylint: disable=R0801
"""
Fast API for the likes controller
"""
from fastapi import HTTPException, APIRouter, Header
import httpx

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.queries_like import *

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from control.common_setup import *

router = APIRouter()

@router.post("/likes", tags=["Likes"])
async def api_create_like(post_id: int, token: str = Header(...)):
    """
    Creates a new like.
    """
    user = await get_user_from_token(token)
    create_like(post_id, user.get("id"))
    return {"message": "Like created successfully"}

@router.get("/likes/post/{post_id}", tags=["Likes"])
async def get_likes(post_id: int, token: str = Header(...)):
    """
    Retrieve the user IDs of users who liked a specific post.
    """
    user = await get_user_from_token(token)
    users = get_likes_from_post(post_id)
    return generate_response_users_with_user_from_back_user(users)

@router.get("/likes/post/{post_id}/count", tags=["Likes"])
async def get_number_of_likes(post_id: int, token: str = Header(...)):
    """
    Get the number of likes for a specific post.
    """
    user = await get_user_from_token(token)
    likes = get_the_number_of_likes(post_id)
    return likes

@router.get("/likes/user/", tags=["Likes"])
async def get_likes_user(token: str = Header(...)):
    """
    Retrieve the post IDs that a specific user has liked.
    """
    user = await get_user_from_token(token)
    posts = get_user_likes(user.get("id"))
    return generate_response_posts_with_users_from_db(posts)

@router.delete("/likes/user/post/{post_id}", tags=["Likes"])
async def api_delete_like(post_id: int, token: str = Header(...)):
    """
    Deletes a like given by the user to a specific post.
    """
    user = await get_user_from_token(token)
    delete_like(user.get("id"), post_id)
    return {"message": "Like deleted successfully"}

@router.get("/likes", tags=["Likes"])
def get_all_likes():
    """
    Retrieve all likes in the system.
    """
    all_likes = get_all_the_likes()
    likes_data = [{"user_id": like.user_id, "post_id": like.id_post} for like in all_likes]
    return likes_data


