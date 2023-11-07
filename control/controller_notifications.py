
"""
Module for the notifications controller
"""
from fastapi import APIRouter, HTTPException, Header
from control.common_setup import NotificationRequest, get_user_from_token, send_push_notifications

# pylint: disable=C0114, W0401, W0614, E0602, E0401
from repository.queries.queries_notifications import *

router = APIRouter()

# pylint disable=W0511
#TODO:
# En el header ademas de recibir el token del usuario
# deberia recibir el token de expo para poder ver
# si tiene permisos para enviar notificaciones
@router.post("/notifications/save/{device_token}", tags=["Notifications"])
async def api_save_device_token(device_token: str, token: str = Header(...)):
    """
    Save the device token of the user
    """
    try:
        user = await get_user_from_token(token)
        response = create_device_token(int(user.get("id")), device_token)
        return {"mensaje": "token stored successfully"}
    except Exception as error:
        return HTTPException(status_code=500, detail=f"Error saving token: {str(error)}")


@router.delete("/notifications/{device_token}", tags=["Notifications"])
async def api_delete_device_token(token: str = Header(...)):
    """
    Delete the device token of the user
    """
    try:
        user = await get_user_from_token(token)
        response = delete_device_token(int(user.get("id")))
        return {"mensaje": "token delete successfully"}
    except Exception as error:
        return HTTPException(status_code=500, detail=f"Failed to send delete token: {str(error)}")


@router.post("/notifications/push", tags=["Notifications"])
async def api_send_notificacion(notificacionRequest: NotificationRequest, token: str = Header(...)):
    """
    Send a notification to the users
    """
    try:
        _ = await get_user_from_token(token)
        tokens_db = get_device_tokens(notificacionRequest.user_ids_that_receive)
        response = send_push_notifications(tokens_db, notificacionRequest)
        return {"mensaje": "Notification sent successfully"}
    except DatabaseError as db_error:
        raise HTTPException(
            status_code=400, detail="Post doesnt exist or repost already exists"
        ) from db_error
    except Exception as exc:
        return HTTPException(status_code=500, detail=f"Error sending notification: {str(exc)}")
    