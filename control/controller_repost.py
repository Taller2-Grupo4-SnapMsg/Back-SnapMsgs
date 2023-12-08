"""
This file contains the controller for the reposts.
"""
from fastapi import APIRouter, Depends

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.queries_reposts import *

from repository.errors import ThisUserIsBlocked

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from control.common_setup import *

from control.utils.tracer import tracer
from control.utils.logger import logger

router = APIRouter()


@router.post("/reposts/{post_id}", tags=["Reposts"])
@tracer.start_as_current_span("Create a repost")
def api_create_repost(
    post_id: int,
    user: callable = Depends(get_user_from_token),
):
    """
    Creates a new repost.
    """
    try:
        create_repost(post_id, user.get("id"))
        logger.info(
            "User %s created repost of post %s successfully", user.get("email"), post_id
        )
        return {"message": "Repost created successfully"}

    except DatabaseError as db_error:
        logger.info(
            "User %s tried to repost post %s but got db error: %s",
            user.get("email"),
            post_id,
            str(db_error),
        )
        raise HTTPException(
            status_code=400, detail="Post doesnt exist or repost already exists"
        ) from db_error
    except UserWithouPermission as error:
        logger.info(
            "User %s tried to repost post %s but user doesnt have permissions",
            user.get("email"),
            post_id,
        )
        raise HTTPException(status_code=403, detail=str(error)) from error
    except ThisUserIsBlocked as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    except RepostAlreadyMade as error:
        logger.info(
            "User %s tried to repost post %s but user had already reposted that post",
            user.get("email"),
            post_id,
        )
        raise HTTPException(status_code=409, detail=str(error)) from error
    except Exception as error:
        logger.info(
            "User %s got an exception while trying to repost post %s: %s",
            user.get("email"),
            post_id,
            str(error),
        )
        raise HTTPException(status_code=500, detail=str(error)) from error


# pylint: disable=R0801
# I disable the "Similar lines in 2 files"
@router.delete("/reposts/from_post/{post_id}", tags=["Reposts"])
@tracer.start_as_current_span("Remove a repost from a post")
def api_delete_respost_from_post(
    post_id: int,
    user: callable = Depends(get_user_from_token),
):
    """
    Deletes a repost of the post_id made by the user.
    """
    try:
        delete_users_repost_from_post(post_id, user.get("id"))
        logger.info(
            "User %s deleted repost of post %s successfully", user.get("email"), post_id
        )
        return {"message": "Repost deleted successfully"}
    except PostNotFound as error:
        logger.error(
            "User %s tried to delete repost of post %s but post not found",
            user.get("email"),
            post_id,
        )
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ThisUserIsBlocked as error:
        logger.error(
            "User %s tried to delete repost of post %s but user is blocked",
            user.get("email"),
            post_id,
        )
        raise HTTPException(status_code=403, detail=str(error)) from error
    except UserWithouPermission as error:
        logger.error(
            "User %s tried to delete repost of post %s but user doesnt have permissions",
            user.get("email"),
            post_id,
        )
        raise HTTPException(status_code=403, detail=str(error)) from error
    except Exception as error:
        logger.error(
            "User %s got an exception while trying to delete repost of post %s: %s",
            user.get("email"),
            post_id,
            str(error),
        )
        raise HTTPException(status_code=500, detail=str(error)) from error


@router.delete("/reposts/{repost_id}", tags=["Reposts"])
@tracer.start_as_current_span("Remove a repost")
def api_delete_respost(
    repost_id: int,
    user: callable = Depends(get_user_from_token),
):
    """
    Deletes a repost given by the user to a specific post.
    """
    try:
        delete_repost(repost_id, user.get("id"))
        logger.info(
            "User %s deleted repost %s successfully", user.get("email"), repost_id
        )
        return {"message": "Repost deleted successfully"}
    except PostNotFound as error:
        logger.error(
            "User %s tried to delete repost %s but repost not found",
            user.get("email"),
            repost_id,
        )
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ThisUserIsBlocked as error:
        logger.error(
            "User %s tried to delete repost of post %s but user is blocked",
            user.get("email"),
            repost_id,
        )
        raise HTTPException(status_code=403, detail=str(error)) from error
    except UserWithouPermission as error:
        logger.error(
            "User %s tried to delete repost of post %s but user is blocked",
            user.get("email"),
            repost_id,
        )
        raise HTTPException(status_code=403, detail=str(error)) from error
    except Exception as error:
        logger.error(
            "User %s got an exception while trying to delete repost %s: %s",
            user.get("email"),
            repost_id,
            str(error),
        )
        raise HTTPException(status_code=500, detail=str(error)) from error
