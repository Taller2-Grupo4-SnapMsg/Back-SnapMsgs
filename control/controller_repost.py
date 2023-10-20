"""
This file contains the controller for the reposts.
"""
from fastapi import APIRouter, Header

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.queries_reposts import *

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from control.common_setup import *

router = APIRouter()


@router.post("/reposts/{repost_id}", tags=["Reposts"])
async def api_create_repost(repost_id: int, token: str = Header(...)):
    """
    Creates a new repost.
    """
    try:
        user = await get_user_from_token(token)
        create_repost(repost_id, user.get("id"))

    except DatabaseError as db_error:
        raise HTTPException(
            status_code=400, detail="Post doesnt exist or repost already exists"
        ) from db_error
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error
    return {"message": "Repost created successfully"}


@router.delete("/reposts/{repost_id}", tags=["Reposts"])
async def api_delete_respost(repost_id: int, token: str = Header(...)):
    """
    Deletes a repost given by the user to a specific post.
    """
    try:
        user = await get_user_from_token(token)
        delete_repost(repost_id, user.get("id"))

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error
    return {"message": "Repost deleted successfully"}
