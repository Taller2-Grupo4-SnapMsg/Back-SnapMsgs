"""
This file contains the logic to send notifications to users
"""
from control.common_setup import HTTPException
from exponent_server_sdk import (
    DeviceNotRegisteredError,
    PushClient,
    PushMessage,
    PushServerError,
    PushTicketError,
)
import os
import requests
from requests.exceptions import ConnectionError, HTTPError
import rollbar
from fastapi import APIRouter, Header

#expo = Expo()
# Optionally providing an access token within a session if you have enabled push security

router = APIRouter()

session = requests.Session()
session.headers.update(
    {
        "Authorization": f"Bearer e0ebae00-8a3b-4632-8f56-d193330d6aa4",
        "accept": "application/json",
        "accept-encoding": "gzip, deflate",
        "content-type": "application/json",
    }
)

def send_push_message(token, message, extra=None):
    try:
        response = PushClient(session=session).publish(
            PushMessage(to=token,
                        body=message,
                        data=extra))
    except PushServerError as exc:
        # Encountered some likely formatting/validation error.
        print("some likely formatting/validation error")
        rollbar.report_exc_info(
            extra_data={
                'token': token,
                'extra': extra,
                'errors': exc.errors,
                'response_data': exc.response_data,
            })
        raise
    except (ConnectionError, HTTPError) as exc:
        # Encountered some Connection or HTTP error - retry a few times in
        print("some Connection or HTTP error")
        # case it is transient.
        rollbar.report_exc_info(
            extra_data={'token': token, 'message': message, 'extra': extra})
        raise exc

    try:
        # We got a response back, but we don't know whether it's an error yet.
        # This call raises errors so we can handle them with normal exception
        # flows.
        response.validate_response()
    except DeviceNotRegisteredError:
        print("DeviceNotRegisteredError")
        raise HTTPException(status_code=500, detail=f"DeviceNotRegisteredError: {token}")
        # Mark the push token as inactive
        
    except PushTicketError as exc:
        print("PushTicketError")
        rollbar.report_exc_info(
            extra_data={
                'token': token,
                'message': message,
                'extra': extra,
                'push_response': exc.push_response._asdict(),
            })
        raise exc
    #return response