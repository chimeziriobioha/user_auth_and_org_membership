from uuid import uuid4
from datetime import datetime, timezone
from flask_jwt_extended import create_access_token, create_refresh_token


from maincode.appstrings import lcl


UNSUCCESSFUL_REGISTER_USER_RESPONSE = {
    "status": "Bad request",
    "message": "Registration unsuccessful",
    "statusCode": 400
}


UNSUCCESSFUL_LOGIN_USER_RESPONSE = {
    "status": "Bad request",
    "message": "Authentication failed",
    "statusCode": 401
}


UNSUCCESSFUL_REGISTER_ORG_RESPONSE = {
    "status": "Bad Request",
    "message": "Client error",
    "statusCode": 400
}


SUCCESSFUL_ADD_USER_TO_ORG_RESPONSE = {
    "status": "success",
    "message": "User added to organisation successfully",
}


def is_eq(val1, val2):
    return val1 == val2


def not_eq(val1, val2):
    return val1 != val2


def aware_utcnow():
    """Return an aware datetime.utcnow"""
    return datetime.now(timezone.utc)


def jwt_error(msg, err):
    return {
        lcl.message: msg,
        lcl.error: err
    }


def create_new_jwt_token(identity, refresh=False):
    if refresh:
        # Refresh existing user token
        return create_refresh_token(identity)
    # Create new user token
    return create_access_token(identity=identity, fresh=True)


def generate_new_org_id(Org):
    new_id = str(uuid4()).replace('-', '')
    while True:
        if Org.get_self(new_id):
            continue
        return new_id


def generate_new_user_id(Usr):
    new_id = str(uuid4()).replace('-', '')
    while True:
        if Usr.get_self(new_id):
            continue
        return new_id