import os
from datetime import datetime, timedelta
from functools import wraps
import jwt
from flask import request
from api.utils.exception import AuthRequired, DecodeError, ExpiredSignatureError, BaseJWTError

JWT_SECRET = os.environ.get("JWT_SECRET", "secret")
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")
JWT_EXP_DELTA_SECONDS = os.environ.get("JWT_EXP_DELTA_SECONDS", 86000)


def authenticate_jwt(func):
    """
    :return:
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        _validate_jwt(request.headers)
        return func(*args, **kwargs)
    return wrapper


def _validate_jwt(headers):
    """
    :param headers:
    :return:
    """
    authorization = headers.get("Authorization", None)
    if authorization is None:
        raise AuthRequired
    try:
        JWT(jwt.decode(authorization, JWT_SECRET, algorithms=[JWT_ALGORITHM]))
    except jwt.DecodeError:
        raise DecodeError
    except jwt.ExpiredSignatureError:
        raise ExpiredSignatureError
    except Exception:
        raise BaseJWTError


def generate_jwt(user):
    """
    :return:
    """
    payload = {
        "user_id": user["id"],
        "exp": datetime.utcnow() + timedelta(seconds=JWT_EXP_DELTA_SECONDS)
    }
    token = jwt.encode(payload, JWT_SECRET, JWT_ALGORITHM)
    return token.decode('utf-8')


class JWT:
    details = {}

    def __init__(self, _jwt):
        """
        :param _jwt:
        """
        JWT.details = _jwt
