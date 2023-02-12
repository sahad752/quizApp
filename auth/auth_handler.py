
import jwt
import time


def decodeJWT(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, "secret", algorithms="HS256")
        return decoded_token 
    except:
        return {}