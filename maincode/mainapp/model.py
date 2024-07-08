from datetime import datetime
from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import JSON

from maincode.mainapp import utils as au
from maincode.appstrings import ccl, lcl
from maincode import db, bcrypt, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


users_organisations_table = db.Table(
    "users_organisations",
    db.Model.metadata,
    db.Column('users_id', db.String, db.ForeignKey('users.id'), primary_key=True),
    db.Column('organisations_id', db.String, db.ForeignKey('organisations.id'), primary_key=True),
    db.Column('created_on', db.DateTime, default=au.aware_utcnow)
)


class User(db.Model, UserMixin):
    """"""
    # -----NOTE----- #
    # Though python naming convention is ``some_name``
    # The task (in .task.txt) directs using ``someName``
    # To avoid issues, I'm sticking to the JS style
    # As they say: "once beaten, twice shy 😊"
    # -----End NOTE----- #
    __tablename__ = "users"

    id = db.Column(db.String, primary_key=True)
    userId = db.Column(db.String, nullable=False, unique=True)
    firstName = db.Column(db.String, nullable=False)
    lastName = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    _accessTokens = db.Column(JSON, nullable=False)
    phone = db.Column(db.String)
    created_on = db.Column(db.DateTime, nullable=False, default=au.aware_utcnow)
    # .........
    # Have to sacrifice `load="dynamic"` in order to visualize relationships in flask-admin
    organisations_created = db.relationship(
        'Organisation', backref=lcl.creator, foreign_keys='Organisation.creatorId')
    organisations = db.relationship(
        'Organisation', secondary=users_organisations_table, back_populates=lcl.users)

    def __init__(self, userId, firstName, lastName, email, password, accessToken, phone=None):

        self.id = userId
        self.email = email
        self.phone = phone
        self.userId = userId
        self.lastName = lastName
        self.firstName = firstName
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
        self._accessTokens = [{
            lcl.user_id: userId, 
            lcl.token: accessToken, 
            lcl.datetime: au.aware_utcnow().isoformat()
        }]
    
    # def update_password(self):
    #     """Arbitrary password update"""
    #     self.password = bcrypt.generate_password_hash("mypassword").decode('utf-8')
    #     db.session.commit()

    def confirm_password(self, password):
        return bcrypt.check_password_hash(self.password, password)
    
    @property
    def current_access_token(self):
        return self._accessTokens[-1][lcl.token]
    
    @property
    def current_access_token_datetime(self):
        return datetime.fromisoformat(self._accessTokens[-1][lcl.datetime])
    
    @property
    def default_org_name(self):
        return f"{self.firstName}'s {ccl.ORGANISATION}"
    
    def add_default_organisation(self, description):
        default_org = Organisation(
            creatorId=self.id,
            description=description,
            name=self.default_org_name,
            orgId=au.generate_new_org_id(Organisation),
        )
        db.session.add(default_org)
        return default_org
    
    @property
    def default_org(self):
        return Organisation.query.filter_by(name=self.default_org_name).first()
    
    @staticmethod
    def get_self(user_id):
        return User.query.filter_by(id=user_id).first()
    
    def to_dict(self):
        return {
            "userId": self.userId,
            "firstName": self.firstName,
            "lastName": self.lastName,
            "email": self.email,
            "phone": self.phone,
        }
    
    @property
    def all_organisations(self) -> list:
        return [o for o in Organisation.query if self in o.users or self == o.creator]
    
    @property
    def users_in_all_organisations(self) -> list:
        return [u for o in self.all_organisations for u in o.users]
    
    def set_new_access_token(self):
        self._accessTokens = [{
            lcl.user_id: self.id, 
            lcl.token: au.create_new_jwt_token(self.id), 
            lcl.datetime: au.aware_utcnow().isoformat(),
        }]
        db.session.commit()


class Organisation(db.Model):
    """"""
    # -----NOTE----- #
    # Though python naming convention is ``some_name``
    # The task (in .task.txt) directs using ``someName``
    # To avoid issues, I'm sticking to the JS style
    # As they say: "once beaten, twice shy 😊"
    # -----End NOTE----- #
    __tablename__ = "organisations"

    id = db.Column(db.String, primary_key=True)
    orgId = db.Column(db.String, nullable=False, unique=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    created_on = db.Column(db.DateTime, nullable=False, default=au.aware_utcnow)
    # .........
    creatorId = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    users = db.relationship('User', secondary=users_organisations_table, 
                            back_populates=lcl.organisations, lazy=lcl.dynamic)

    def __init__(self, orgId, name, creatorId, description=None):

        self.id = orgId
        self.name = name
        self.orgId = orgId
        self.creatorId = creatorId
        self.description = description
    
    @staticmethod
    def get_self(org_id):
        return Organisation.query.filter_by(id=org_id).first()
    
    def to_dict(self):
        return {
            "orgId": self.orgId,
            "name": self.name,
            "description": self.description
        }