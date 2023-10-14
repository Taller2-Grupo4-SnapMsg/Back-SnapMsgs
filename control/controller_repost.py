from fastapi import APIRouter, Header
from repository.queries.queries_repost import *
from control.common_setup import *

router = APIRouter()

@router.post("/reposts", tags=["Reposts"])
async def api_create_repost(post_id: int, token: str = Header(...)):
    """
    Creates a new repost.
    """
    user = await get_user_from_token(token)
    create_repost(post_id, user.get("id"))
    return {"message": "Repost created successfully"}


@router.delete("/reposts/user/post/{post_id}", tags=["Reposts"])
async def api_delete_respost(post_id: int, token: str = Header(...)):
    """
    Deletes a repost given by the user to a specific post.
    """
    user = await get_user_from_token(token)
    delete_repost(user.get("id"), post_id)
    return {"message": "Repost deleted successfully"}
