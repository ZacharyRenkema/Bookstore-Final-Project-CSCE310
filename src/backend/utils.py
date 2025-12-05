# utils.py
import jwt
from flask import request
from models import User
import config


def get_current_user():
    auth_header = request.headers.get("Authorization", "")
    print("AUTH HEADER RAW:", repr(auth_header))  # DEBUG

    if not auth_header.startswith("Bearer "):
        print("No Bearer token found in header")   # DEBUG
        return None

    token = auth_header.split(" ", 1)[1].strip()
    print("TOKEN RECEIVED:", token)               # DEBUG

    try:
        payload = jwt.decode(token, config.JWT, algorithms=["HS256"])
        print("DECODED PAYLOAD:", payload)        # DEBUG
    except jwt.PyJWTError as e:
        print("JWT DECODE ERROR:", e)             # DEBUG
        return None

    user_id = payload.get("sub")
    if user_id is None:
        print("No 'sub' in payload")              # DEBUG
        return None

    try:
        user_id = int(user_id)                    # <-- convert back to int
    except ValueError:
        print("SUB is not a valid int:", user_id)
        return None

    user = User.query.get(user_id)
    print("LOOKED-UP USER:", user)                # DEBUG
    return user
