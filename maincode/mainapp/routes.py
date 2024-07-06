from flask import Blueprint
from markupsafe import Markup


from maincode import db
from maincode.mainapp.model import User, Organisation


mainapp = Blueprint("mainapp", __name__)


@mainapp.route("/")
def home():
    """Just to have something on the home page"""
    return Markup(
        "<h1>Hello, Welcome!</h1> <br>"
        "<h3>This is <a href='https://hng.tech'>HNG11</a> Stage Two Task by Chimeziri Obioha.</h3>"
    )


def register_user(data):
    
    # Initialise user
    user = User(
        email=data['email'],
        phone=data['phone'],
        userId=data['userId'],
        lastName=data['lastName'],
        password=data['password'],
        firstName=data['firstName'],
        accessToken=data['accessToken']
    )

    # Add user to session
    db.session.add(user)

    # Create default org for user
    org = user.add_default_organisation("")

    # Commit all
    db.session.commit()

    return user, org
