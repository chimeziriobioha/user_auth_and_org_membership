from flask import jsonify
from flask.views import MethodView
from flask_login import login_user
from flask_smorest import Blueprint as smBlueprint, abort as smAbort
from flask_jwt_extended import (
    # create_refresh_token,
    # create_access_token,
    get_jwt_identity,
    jwt_required,
    # get_jwt,
)

from maincode.mainapp import utils as au
from maincode.mainapp.model import User, Organisation
from maincode.mainapi.schemas import UserSchema, OrganisationSchema, UserLoginSchema


sm_accounts = smBlueprint("Accounts", __name__,
                          description="Accounts creation and operations")


# User urls
LOGIN_USER_URL = "/auth/login"
REGISTER_USER_URL = "/auth/register"
GET_USER_URL = "/api/users/<string:id>"

# Organisation urls
LIST_ORGS_URL = "/api/organisations"
REGISTER_ORG_URL = "/api/organisations"
GET_ORG_URL = "/api/organisations/<string:orgId>"
ADD_USER_TO_ORG_URL = "/api/organisations/<string:orgId>/users"


def auth_user(user_or_email, password, login=False):
    """Authenticate a `user_or_email` and return the 
    user if everything goes well, else, return an 
    error dict"""
    if isinstance(user_or_email, str):
        user = User.query.filter_by(email=user_or_email).first()
    else:
        user = user_or_email

    if not isinstance(user, User):
        return au.UNSUCCESSFUL_LOGIN_USER_RESPONSE

    if not user.confirm_password(password):
        return au.UNSUCCESSFUL_LOGIN_USER_RESPONSE

    if login:
        login_user(user)

    return user


@sm_accounts.route(REGISTER_USER_URL)
class RegisterUser(MethodView):

    @sm_accounts.arguments(UserSchema)
    @sm_accounts.response(201, UserSchema)
    def post(self, data):
        """REGISTER NEW USER"""
        try:
            user, _ = mainapp.routes.register_user(data)

            return jsonify({
                "status": "success",
                "message": "Registration successful",
                "data": {
                    "accessToken": user.current_access_token,
                    "user": user.to_dict()
                }
            })
        except TypeError:
            # smAbort(400, message="Unable to complete create user at this time")
            # return jsonify({
            #     "status": "Bad request",
            #     "message": "Registration unsuccessful",
            #     "statusCode": 400
            # })
            return jsonify(au.UNSUCCESSFUL_REGISTER_USER_RESPONSE)


@sm_accounts.route(LOGIN_USER_URL)
class LoginUser(MethodView):

    @sm_accounts.arguments(UserLoginSchema)
    @sm_accounts.response(200, UserSchema)
    def post(self, data):
        """LOGIN USER"""
        try:
            user = auth_user(data['email'], data['password'], login=True)

            return jsonify({
                "status": "success",
                "message": "Login successful",
                "data": {
                    "accessToken": user.current_access_token,
                    "user": user.to_dict()
                }
            })
        except TypeError:
            # smAbort(400, message="Unable to complete create user at this time")
            return jsonify(au.UNSUCCESSFUL_LOGIN_USER_RESPONSE)


@sm_accounts.route(GET_USER_URL)
class GetUser(MethodView):

    @jwt_required()
    @sm_accounts.response(200, UserSchema)
    def get(self, id):
        """GET PARTICULAR USER"""
        try:
            # return User.query.filter_by(id=id).first()
            return User.get_self(id)
        except TypeError:
            smAbort(400, message="Could not get user")


@sm_accounts.route(LIST_ORGS_URL)
class ListOrgs(MethodView):

    @jwt_required()
    @sm_accounts.response(200, OrganisationSchema(many=True))
    def get(self):
        """LIST ALL ORGS"""
        try:
            return Organisation.query.all()
        except TypeError:
            smAbort(500, message="Unable to get orgs at this time")


@sm_accounts.route(GET_ORG_URL)
class GetOrg(MethodView):

    @jwt_required()
    @sm_accounts.response(200, OrganisationSchema)
    def get(self, orgId):
        """GET PARTICULAR ORGANISATION"""
        try:
            # return Organisation.query.filter_by(id=orgId).first()
            return Organisation.get_self(orgId)
        except TypeError:
            smAbort(400, message="Could not get org")


@sm_accounts.route(REGISTER_ORG_URL)
class RegisterOrg(MethodView):

    @jwt_required()
    @sm_accounts.arguments(OrganisationSchema)
    @sm_accounts.response(201, OrganisationSchema)
    def post(self, data):
        """REGISTER NEW ORG"""
        try:
            data.update({"creatorId": get_jwt_identity()})

            org, creator = mainapp.routes.register_org(data)

            print(data)
            print(creator.to_dict())

            return jsonify({
                "status": "success",
                "message": "Organisation created successfully",
                "data": org.to_dict()
            })
        except TypeError:
            # smAbort(400, message="Unable to complete create user at this time")
            return jsonify(au.UNSUCCESSFUL_REGISTER_ORG_RESPONSE)


@sm_accounts.route(ADD_USER_TO_ORG_URL)
class AddUserToOrg(MethodView):

    @sm_accounts.arguments(UserSchema(only={'userId'}))
    @sm_accounts.response(200, UserSchema)
    def post(self, data, orgId):
        """ADD USER TO ORG"""
        try:
            _, _ = mainapp.routes.add_user_to_org(data['userId'], orgId)

            return jsonify(au.SUCCESSFUL_ADD_USER_TO_ORG_RESPONSE)
        except TypeError:
            return {
                "status": "Bad Request",
                "message": "Client error",
                "statusCode": 400
            }


def register_accounts_api(app):
    app.add_url_rule(
        REGISTER_USER_URL, view_func=RegisterUser.as_view("register_user-register_user"))
    app.add_url_rule(
        LOGIN_USER_URL, view_func=LoginUser.as_view("login_user-login_user"))
    app.add_url_rule(
        GET_USER_URL, view_func=GetUser.as_view("get_user-get_user"))
    app.add_url_rule(
        LIST_ORGS_URL, view_func=ListOrgs.as_view("list_orgs-list_orgs"))
    app.add_url_rule(
        GET_ORG_URL, view_func=GetOrg.as_view("get_org-get_org"))
    app.add_url_rule(
        ADD_USER_TO_ORG_URL, view_func=AddUserToOrg.as_view("add_user_to_org_org-add_user_to_org_org"))


from maincode import mainapp  # noqa
