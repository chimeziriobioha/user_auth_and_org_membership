from flask import Blueprint, jsonify, request


from maincode import db
from maincode.appstrings import lcl, ccl
from maincode.mainapp import utils as au
from maincode.mainapp.model import User, Organisation


mainapp = Blueprint("mainapp", __name__)


@mainapp.route("/")
def home():
    """Explain yourself and status"""
    return jsonify({
        lcl.project: "HNG11 [https://hng.tech] Stage Two Task by Chimeziri Obioha",
        lcl.description: "User Authentication & Organisation Membership",
        lcl.documentation: f"{request.base_url}api/ui",
        lcl.status: ccl.ACTIVE
    }), 200


def register_user(data):

    user_id = au.generate_new_user_id(User)
    
    # Initialise user
    user = User(
        userId=user_id,
        email=data['email'],
        phone=data['phone'],
        lastName=data['lastName'],
        password=data['password'],
        firstName=data['firstName'],
        accessToken=au.create_new_jwt_token(user_id)
    )

    # Add user to session
    db.session.add(user)

    # Create default org for user
    org = user.add_default_organisation("")

    # Commit all
    db.session.commit()

    return user, org


def register_org(data):
    
    # Initialise org
    org = Organisation(
        name=data[lcl.name],
        creatorId=data['creatorId'],
        description=data[lcl.description],
        orgId=au.generate_new_org_id(Organisation),
    )

    # Add org to session
    db.session.add(org)

    # Commit all
    db.session.commit()

    return org, org.creator


def add_user_to_org(userId, orgId):

    user = User.get_self(userId)
    if not user:
        return

    org = Organisation.get_self(orgId)
    if not org:
        return
    
    # Add user to org
    org.users.add(user)

    # Commit all
    db.session.commit()

    return user, org
