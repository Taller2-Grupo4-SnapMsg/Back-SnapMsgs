
from fastapi import APIRouter, HTTPException
from control.common_setup import NotificationRequest
from control.send_push_message import send_push_message

router = APIRouter()

@router.post("/notifications", tags=["Notifications"])
async def enviar_notificacion(notificacion: NotificationRequest):
    mensaje = notificacion.mensaje
    usuario_destino = notificacion.usuario_destino
    print(mensaje)
    print(usuario_destino)
    try:
        response = await send_push_message(usuario_destino, mensaje)
        print(response)
        return {"mensaje": "Notificación enviada con éxito", "response": response}
    except Exception as exc:
        return HTTPException(status_code=500, detail=f"Error al enviar la notificación: {str(exc)}")
