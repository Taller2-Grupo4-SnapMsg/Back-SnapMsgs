# pylint: disable=R0801
"""
Fast API for the likes controller
"""
from fastapi import APIRouter, Depends

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.queries_likes import *
from repository.queries.queries_global import get_content_id_from_post

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from control.common_setup import *

from control.utils.tracer import tracer
from control.utils.logger import logger

router = APIRouter()


@router.post("/likes/{post_id}", tags=["Likes"])
@tracer.start_as_current_span("Like a post")
def api_create_like(
    post_id: int,
    user: callable = Depends(get_user_from_token),
):
    """
    Creates a new like.
    """
    try:
        content_id = get_content_id_from_post(post_id)
        create_like(post_id, content_id, user.get("id"))
        logger.info(
            "User %s created like for post %s successfully", user.get("email"), post_id
        )
        return {"message": "Like created successfully"}
    except PostNotFound as error:
        logger.error(
            "User %s tried to like post %s but that post was not found",
            user.get("email"),
            post_id,
        )
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ThisUserIsBlocked as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    except DatabaseError as db_error:
        logger.error(
            "User %s got Database error while trying to create a new like for post id %s: %s",
            user.get("email"),
            post_id,
            str(db_error),
        )
        raise HTTPException(
            status_code=400, detail="Post doesnt exist or like already exists"
        ) from db_error
    except Exception as error:
        logger.error(
            "User %s got an exception while trying to create a like for post with id %s: %s",
            user.get("email"),
            post_id,
            str(error),
        )
        raise HTTPException(status_code=500, detail=str(error)) from error


@router.delete("/likes/{post_id}", tags=["Likes"])
@tracer.start_as_current_span("Remove a like from a post")
def api_delete_like(
    post_id: int,
    user: callable = Depends(get_user_from_token),
):
    """
    Deletes a like given by the user to a specific post.
    """
    try:
        content_id = get_content_id_from_post(post_id)
        delete_like(content_id, user.get("id"))
        logger.info(
            "User %s deleted like for post %s successfully", user.get("email"), post_id
        )
        return {"message": "Like deleted successfully"}
    except LikeNotFound as error:
        logger.error(
            "User %s tried to like post %s but like was not found",
            user.get("email"),
            post_id,
        )
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ThisUserIsBlocked as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    except Exception as error:
        logger.error(
            "User %s got an exception while trying to delete a like for post with id %s: %s",
            user.get("email"),
            post_id,
            str(error),
        )
        raise HTTPException(status_code=500, detail=str(error)) from error
