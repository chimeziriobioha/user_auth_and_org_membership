from flask import Blueprint
from markupsafe import Markup


from maincode import db
from maincode.appstrings import lcl
from maincode.mainapp import utils as au
from maincode.mainapp.model import User, Organisation


mainapp = Blueprint("mainapp", __name__)


@mainapp.route("/")
def home():
    """Just to have something on the home page"""
    return Markup(
        "<h1>Hello, Welcome!</h1> <br>"
        "<h3>This is <a href='https://hng.tech'>HNG11</a> Stage Two Task by Chimeziri Obioha.</h3>"
    )


@mainapp.route("/auth/register")
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
