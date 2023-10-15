# pylint: disable=R0801
"""
Fast API for the likes controller
"""
from fastapi import APIRouter, Header

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


@router.delete("/likes/{post_id}", tags=["Likes"])
async def api_delete_like(post_id: int, token: str = Header(...)):
    """
    Deletes a like given by the user to a specific post.
    """
    user = await get_user_from_token(token)
    delete_like(user.get("id"), post_id)
    return {"message": "Like deleted successfully"}




