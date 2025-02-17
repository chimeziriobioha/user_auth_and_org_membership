from flask import jsonify
from flask.views import MethodView
from flask_login import login_user
from flask_smorest import Blueprint as smBlueprint
from flask_jwt_extended import (
    get_jwt_identity,
    jwt_required,
)

from maincode.appstrings import lcl
from maincode.mainapp import utils as au
from maincode.mainapp.model import User, Organisation
from maincode.mainapi.schemas import UserSchema, OrganisationSchema, \
    UserLoginSchema, AddUserToOrgSchema


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
        return jsonify(au.UNSUCCESSFUL_LOGIN_USER_RESPONSE), 401

    if not user.confirm_password(password):
        return jsonify(au.UNSUCCESSFUL_LOGIN_USER_RESPONSE), 401

    if login:
        login_user(user)

    return user


@sm_accounts.route(REGISTER_USER_URL)
class RegisterUser(MethodView):

    @sm_accounts.arguments(UserSchema)
    @sm_accounts.response(201, UserSchema)
    def post(self, data):
        """REGISTER NEW USER"""

        errors = au.check_regiter_user_data(data)
        if errors[lcl.errors]:
            return jsonify(errors), 422
        
        if User.query.filter_by(email=data[lcl.email]).first():
            errors[lcl.errors].append({lcl.field: lcl.email, lcl.message: "User with email exists"})
        
        if not au.is_valid_email_format(data[lcl.email]):
            errors[lcl.errors].append({lcl.field: lcl.email, lcl.message: "Invalid email"})
        
        if data.get(lcl.phone) and not data[lcl.phone].replace('+', '').replace('-', '').isnumeric():
            errors[lcl.errors].append({lcl.field: lcl.phone, lcl.message: "Invalid phone number"})
        
        if errors[lcl.errors]:
            return jsonify(errors), 422
        
        try:
            user, _ = mainapp.routes.register_user(data)

            return jsonify({
                "status": "success",
                "message": "Registration successful",
                "data": {
                    "accessToken": user.current_access_token,
                    "user": user.to_dict()
                }
            }), 201
        except Exception as e: # noqa
            return jsonify(au.UNSUCCESSFUL_REGISTER_USER_RESPONSE), 400
        except: # noqa
            return jsonify(au.UNSUCCESSFUL_REGISTER_USER_RESPONSE), 400


@sm_accounts.route(LOGIN_USER_URL)
class LoginUser(MethodView):

    @sm_accounts.arguments(UserLoginSchema)
    @sm_accounts.response(200, UserSchema)
    def post(self, data):
        """LOGIN USER"""
        
        errors = au.check_login_data(data)
        if errors[lcl.errors]:
            return jsonify(errors), 422
        
        try:
            user = auth_user(data[lcl.email], data[lcl.password], login=True)

            user.set_new_access_token()

            return jsonify({
                "status": "success",
                "message": "Login successful",
                "data": {
                    "accessToken": user.current_access_token,
                    "user": user.to_dict()
                }
            }), 200
        except Exception as e: # noqa
            return jsonify(au.UNSUCCESSFUL_LOGIN_USER_RESPONSE), 401
        except: # noqa
            return jsonify(au.UNSUCCESSFUL_LOGIN_USER_RESPONSE), 401


@sm_accounts.route(GET_USER_URL)
class GetUser(MethodView):

    @jwt_required()
    @sm_accounts.response(200, UserSchema)
    def get(self, id):
        """GET PARTICULAR USER"""
        try:
            requested_user = User.get_self(id)
            current_user = User.get_self(get_jwt_identity())
            if (not current_user) or (not requested_user):
                return jsonify(au.UNSUCCESSFUL_GET_USER_RESPONSE), 400
            
            if  requested_user != current_user \
                and requested_user not in current_user.users_in_all_organisations:
                return jsonify(au.UNSUCCESSFUL_GET_USER_RESPONSE), 400

            return jsonify({
                "status": "success",
                "message": "User fetched successfully",
                "data": requested_user.to_dict()
            }), 200
        except Exception as e: # noqa
            return jsonify(au.UNSUCCESSFUL_GET_USER_RESPONSE), 400
        except: # noqa
            return jsonify(au.UNSUCCESSFUL_GET_USER_RESPONSE), 400


@sm_accounts.route(LIST_ORGS_URL)
class ListOrgs(MethodView):

    @jwt_required()
    @sm_accounts.response(200, OrganisationSchema(many=True))
    def get(self):
        """LIST ALL ORGS"""
        try:
            user_id = get_jwt_identity()

            user = User.get_self(user_id)

            orgs = [
                o.to_dict() for o in Organisation.query
                if user in o.users or user == o.creator
            ]
            
            return jsonify({
                "status": "success",
                "message": "Orgs fetched successfully",
                "data": {
                    "organisations": orgs
                }
            }), 200
        except Exception as e: # noqa
            return jsonify(au.UNSUCCESSFUL_LIST_ORGS_RESPONSE), 400
        except: # noqa
            return jsonify(au.UNSUCCESSFUL_LIST_ORGS_RESPONSE), 400


@sm_accounts.route(GET_ORG_URL)
class GetOrg(MethodView):

    @jwt_required()
    @sm_accounts.response(200, OrganisationSchema)
    def get(self, orgId):
        """GET PARTICULAR ORGANISATION"""
        try:
            org = Organisation.get_self(orgId)
            if not org:
                return jsonify(au.UNSUCCESSFUL_GET_ORG_RESPONSE), 400
            
            return jsonify({
                "status": "success",
                "message": "Org fetched successfully",
                "data": org.to_dict()
            }), 200
        except Exception as e: # noqa
            return jsonify(au.UNSUCCESSFUL_GET_ORG_RESPONSE), 400
        except: # noqa
            return jsonify(au.UNSUCCESSFUL_GET_ORG_RESPONSE), 400


@sm_accounts.route(REGISTER_ORG_URL)
class RegisterOrg(MethodView):

    @jwt_required()
    @sm_accounts.arguments(OrganisationSchema)
    @sm_accounts.response(201, OrganisationSchema)
    def post(self, data):
        """REGISTER NEW ORG"""
        if not data.get(lcl.name):
            return jsonify({lcl.errors: [{lcl.field: lcl.name, lcl.message: "Name is required"}]}), 422

        try:
            data.update({"creatorId": get_jwt_identity()})

            org, _ = mainapp.routes.register_org(data)

            return jsonify({
                "status": "success",
                "message": "Organisation created successfully",
                "data": org.to_dict()
            }), 201
        except Exception as e: # noqa
            return jsonify(au.UNSUCCESSFUL_REGISTER_ORG_RESPONSE), 400
        except: # noqa
            return jsonify(au.UNSUCCESSFUL_REGISTER_ORG_RESPONSE), 400


@sm_accounts.route(ADD_USER_TO_ORG_URL)
class AddUserToOrg(MethodView):

    @sm_accounts.arguments(AddUserToOrgSchema(only={'userId'}))
    def post(self, data, orgId):
        """ADD USER TO ORG"""
        if not data.get('userId'):
            return jsonify({lcl.errors: [{lcl.field: 'userId', lcl.message: "UserId is required"}]}), 422
        
        try:
            result = mainapp.routes.add_user_to_org(data.get('userId'), orgId)
            if not isinstance(result, tuple):
                return jsonify(au.UNSUCCESSFUL_ADD_USER_TO_ORG_RESPONSE), 401

            return jsonify(au.SUCCESSFUL_ADD_USER_TO_ORG_RESPONSE), 200
        except Exception as e: # noqa
            return jsonify(au.UNSUCCESSFUL_ADD_USER_TO_ORG_RESPONSE), 401
        except: # noqa
            return jsonify(au.UNSUCCESSFUL_ADD_USER_TO_ORG_RESPONSE), 401


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
