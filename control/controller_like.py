# pylint: disable=R0801
"""
Fast API for the likes controller
"""
from fastapi import APIRouter, Header

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.queries_likes import *
from repository.queries.queries_global import get_content_id_from_post

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from control.common_setup import *
from control.utils.tracer import tracer

router = APIRouter()


@router.post("/likes/{post_id}", tags=["Likes"])
@tracer.start_as_current_span("Like a post")
def api_create_like(post_id: int, token: str = Header(...)):
    """
    Creates a new like.
    """
    try:
        user = get_user_from_token(token)
        content_id = get_content_id_from_post(post_id)
        create_like(post_id, content_id, user.get("id"))
        return {"message": "Like created successfully"}
    except PostNotFound as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except DatabaseError as db_error:
        raise HTTPException(
            status_code=400, detail="Post doesnt exist or like already exists"
        ) from db_error
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


@router.delete("/likes/{post_id}", tags=["Likes"])
@tracer.start_as_current_span("Remove a like from a post")
def api_delete_like(post_id: int, token: str = Header(...)):
    """
    Deletes a like given by the user to a specific post.
    """
    try:
        user = get_user_from_token(token)
        content_id = get_content_id_from_post(post_id)
        delete_like(content_id, user.get("id"))
        return {"message": "Like deleted successfully"}
    except LikeNotFound as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error
