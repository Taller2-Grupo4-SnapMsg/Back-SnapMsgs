from exponent_server_sdk import DeviceNotRegisteredError, PushClient, PushMessage, PushServerError, PushTicketError
import os
import requests


def send_push_message(token, message, extra=None):
    session = requests.Session()
    print("EXPO_TOKEN")
    print(os.getenv('EXPO_TOKEN'))
    session.headers.update({
        "Authorization": f"Bearer {os.getenv('EXPO_TOKEN')}",
        "accept": "application/json",
        "accept-encoding": "gzip, deflate",
        "content-type": "application/json",
    })

    try:
        push_message = PushMessage(to=token, body=message, data=extra)
        print(push_message)
        response = PushClient(session=session).publish(push_message)
    except PushServerError as exc:
        print("PushServerError:", exc.errors)
        print("Response data:", exc.response_data)
        raise
    except (ConnectionError, requests.exceptions.HTTPError) as exc:
        print("Connection/HTTP Error:", exc)
        raise

    try:
        response.validate_response()
    except DeviceNotRegisteredError:
        print("DeviceNotRegisteredError: Marcar el token como inactivo")
    except PushTicketError as exc:
        print("PushTicketError:", exc.push_response._asdict())
        raise

    return response

token_destinatario = "ExponentPushToken[bhFOjeJADEUXSb66G_a6Ad]"
mensaje = "¡Hola! Esto es una notificación de prueba."
resultado = send_push_message(token_destinatario, mensaje)
print("Resultado de la notificación:", resultado)