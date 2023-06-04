import time
from typing import Dict

import jwt
from decouple import config
from models import User
from db import r


JWT_SECRET = config("SECRET_KEY")
JWT_ALGORITHM = config('ALGORITHM')

    
def token_response(token: str):
    return {
           "access_token": token
    }

# function used for signing the JWT string
def createJWT(user_id: str) -> Dict[str, str]:
    payload = {
        "user_id": user_id,
        "expires": time.time() + 600
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    r.set(token, user_id)
    return token_response(token)


def decodeJWT(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except:
        return {}
    
def get_user_id_from_token(token: str):
    try:
        payload = decodeJWT(token)
        user_id = payload.get("user_id")
        return user_id
    except:
        return None