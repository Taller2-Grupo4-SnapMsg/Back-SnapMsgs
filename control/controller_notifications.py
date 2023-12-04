"""
Module for the notifications controller
"""
from fastapi import APIRouter, HTTPException, Depends

# from control.utils.tracer import tracer
# pylint: disable=C0114, W0401, W0614, E0602, E0401
from control.common_setup import *
from control.common_setup import (
    NotificationRequest,
    get_user_from_token,
    send_push_notifications,
)
from repository.queries.queries_notifications import *

router = APIRouter()


@router.post("/notifications/save/{device_token}", tags=["Notifications"])
# @tracer.start_as_current_span("Save a device token")
def api_save_device_token(
    device_token: str,
    user: callable = Depends(get_user_from_token),
):
    """
    Save the device token of the user
    """
    try:
        create_device_token(int(user.get("id")), device_token)
        return {"mensaje": "token stored successfully"}
    except UserNotFound as error:
        raise HTTPException(
            status_code=404, detail=f"Error saving token: {str(error)}"
        ) from error
    except DatabaseError as db_error:
        raise HTTPException(
            status_code=400, detail="User and token doesnt already exists"
        ) from db_error


@router.delete("/notifications/{device_token}", tags=["Notifications"])
# @tracer.start_as_current_span("Delete a device token")
def api_delete_device_token(
    user: callable = Depends(get_user_from_token),
):
    """
    Delete the device token of the user
    """
    try:
        delete_device_token(int(user.get("id")))
        return {"mensaje": "token delete successfully"}
    except UserNotFound as error:
        raise HTTPException(
            status_code=404, detail=f"Error saving token: {str(error)}"
        ) from error
    except DatabaseError as db_error:
        raise HTTPException(
            status_code=400, detail="User and token doesnt already exists"
        ) from db_error


@router.post("/notifications/push", tags=["Notifications"])
# @tracer.start_as_current_span("Send a notification")
def api_send_notificacion(
    notificacion_request: NotificationRequest,
    _: callable = Depends(get_user_from_token),
):
    """
    Send a notification to the users
    """
    try:
        users_ids_db = get_users_ids_by_emails(
            notificacion_request.user_emails_that_receive
        )
        users_ids = [user.id for user in users_ids_db]
        tokens_db = get_device_tokens(users_ids)
        send_push_notifications(tokens_db, notificacion_request)
        return {"mensaje": "Notification sent successfully"}
    except UserNotFound as error:
        raise HTTPException(
            status_code=404, detail=f"Error saving token: {str(error)}"
        ) from error
    except DatabaseError as db_error:
        raise HTTPException(
            status_code=400, detail="User and token doesnt already exists"
        ) from db_error
