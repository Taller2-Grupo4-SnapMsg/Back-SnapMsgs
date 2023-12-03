"""
This file contains the controller for the reposts.
"""
from fastapi import APIRouter, Header

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.queries_reposts import *

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from control.common_setup import *
from control.utils.tracer import tracer

router = APIRouter()


@router.post("/reposts/{post_id}", tags=["Reposts"])
@tracer.start_as_current_span("Create a repost")
def api_create_repost(post_id: int, token: str = Header(...)):
    """
    Creates a new repost.
    """
    try:
        user = get_user_from_token(token)
        create_repost(post_id, user.get("id"))
        return {"message": "Repost created successfully"}

    except DatabaseError as db_error:
        raise HTTPException(
            status_code=400, detail="Post doesnt exist or repost already exists"
        ) from db_error
    except UserWithouPermission as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    except RepostAlreadyMade as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


@router.delete("/reposts/from_post/{post_id}", tags=["Reposts"])
@tracer.start_as_current_span("Remove a repost from a post")
def api_delete_respost_from_post(post_id: int, token: str = Header(...)):
    """
    Deletes a repost of the post_id made by the user.
    """
    try:
        user = get_user_from_token(token)
        delete_users_repost_from_post(post_id, user.get("id"))
        return {"message": "Repost deleted successfully"}
    except PostNotFound as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except UserWithouPermission as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


@router.delete("/reposts/{repost_id}", tags=["Reposts"])
@tracer.start_as_current_span("Remove a repost")
def api_delete_respost(repost_id: int, token: str = Header(...)):
    """
    Deletes a repost given by the user to a specific post.
    """
    try:
        user = get_user_from_token(token)
        delete_repost(repost_id, user.get("id"))
        return {"message": "Repost deleted successfully"}
    except PostNotFound as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except UserWithouPermission as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error
