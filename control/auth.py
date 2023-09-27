# auth.py

"""
Module dedicated to the authorization of users.
"""

from datetime import datetime, timedelta
import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext

LIFE_TIME_DAYS = 30
LIFE_TIME_MINS = 0
LIFE_TIME_SECS = 0
ENCODING_ALGORITHM = "HS256"

ERROR_TOKEN_EXPIRED = 401
ERROR_INVALID_TOKEN = 401


class AuthHandler:
    """
    Handler for user authentifications.
    """

    security = HTTPBearer()
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    secret = "SO_SECRET"

    def get_password_hash(self, password):
        """
        get a new hash from the password
        """

        return self.pwd_context.hash(password)

    def verify_password(self, plain_password, hashed_password):
        """
        check if the password and the hashed password given match
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def encode_token(self, user_email):
        """
        encode the token with the user email and the expiration date
        """
        payload = {
            "exp": datetime.utcnow()
            + timedelta(
                days=LIFE_TIME_DAYS, minutes=LIFE_TIME_MINS, seconds=LIFE_TIME_SECS
            ),
            "iat": datetime.utcnow(),
            "sub": user_email,
        }

        return jwt.encode(payload, self.secret, algorithm=ENCODING_ALGORITHM)

    def decode_token(self, token):
        """
        decode the token and return the user email
        """
        try:
            payload = jwt.decode(token, self.secret, algorithms=[ENCODING_ALGORITHM])
            return payload["sub"]
        except jwt.ExpiredSignatureError as error:
            raise HTTPException(
                status_code=ERROR_TOKEN_EXPIRED, detail="Signature has expired"
            ) from error
        except jwt.InvalidTokenError as error:
            raise HTTPException(
                status_code=ERROR_INVALID_TOKEN, detail="Invalid token"
            ) from error

    def auth_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security)):
        """
        Wrapper for auth
        """
        # extra level of security
        return self.decode_token(auth.credentials)
