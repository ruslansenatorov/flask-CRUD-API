import jwt
import datetime
from flask import request, jsonify
from infrastructure.config import Config

JWT_SECRET = Config.SECRET_KEY
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRES_MINUTES = 15
REFRESH_TOKEN_EXPIRES_DAYS = 7

def generateToken(email):
    access_token_payload = {
        "email" : email,
        "exp" : datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES)
    }

    access_token = jwt.encode(access_token_payload, JWT_SECRET, algorithm= JWT_ALGORITHM)

    refresh_token_payload = {
        "email" : email,
        "exp" : datetime.datetime.utcnow() + datetime.timedelta(days= REFRESH_TOKEN_EXPIRES_DAYS)
    }

    refresh_token = jwt.encode(refresh_token_payload, JWT_SECRET, algorithm= JWT_ALGORITHM)

    return access_token, refresh_token


def decodeToken(token):

    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms= [JWT_ALGORITHM])
        return decoded
    except jwt.ExpiredSignatureError:
        return {"error" : "Token has expired"}
    except jwt.InvalidTokenError:
        return {"error" : "Invalid token"}
    
def tokenRequired(f):
    #decorater to protect routes with JWT authentication
    # @tokenRequired decorator is used for the protected routes

    def decorator(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({"error" : "Token is missing"}), 401
        

        token.split(" ")[1] if " " in token else token

        decoded = decodeToken(token)

        if "error" in decoded:
            return jsonify(decoded), 401
        
        request.user = decoded['email']
        return f(*args, **kwargs)
    return decorator