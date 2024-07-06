"""
AVAILABLE TO THE PUBLIC
"""
from flask import Blueprint, jsonify, redirect, request

from maincode import jwt
from maincode.config import BaseConfig
from maincode.mainapp import utils as au
from maincode.mainapi.accounts import register_accounts_api


mainapi = Blueprint('mainapi', __name__)


@mainapi.route(f"{BaseConfig.OPENAPI_SWAGGER_UI_PATH}", methods=['GET'])
def openapi_swagger_ui():
    return redirect(f"{request.base_url}{BaseConfig.OPENAPI_SWAGGER_UI_PATH}")


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):  # noqa
    return (jsonify(au.jwt_error("The token has expired.", "token_expired")), 401)


@jwt.invalid_token_loader
def invalid_token_callback(error):  # noqa
    return (jsonify(au.jwt_error("Signature verification failed.", "invalid_token")), 401)


@jwt.unauthorized_loader
def missing_token_callback(error):  # noqa
    return (jsonify(au.jwt_error("No access token in request.", "authorization_required")), 401)


@jwt.needs_fresh_token_loader
def token_not_fresh_callback(jwt_header, jwt_payload):  # noqa
    return (jsonify(au.jwt_error("The token is not fresh.", "fresh_token_required")), 401)


@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):  # noqa
    return (jsonify(au.jwt_error("The token has been revoked.", "token_revoked")), 401)


register_accounts_api(mainapi)
