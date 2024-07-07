import pytest
from flask import request

from maincode import db, create_app, jwt
from maincode.mainapp import utils as au
from maincode.mainapp.model import User, Organisation


@pytest.fixture
def app():
    app = create_app(config_type='testing')
    app_ctx = app.app_context()
    app_ctx.push()
    # Create tables
    db.create_all()
    # Do tests
    yield app
    # Drop tables
    db.drop_all()
    app_ctx.pop()


@pytest.fixture
def client(app):
    # yield test client
    return app.test_client()


unique_user_fields = ["userId", "email"]

required_user_fields = ["userId", "firstName", "lastName", "email", "password"]

u1data = {
	"userId": "", # must be unique
	"firstName": "Chimeziri", # must not be null
	"lastName": "Obioha", # must not be null
	"email": "chimeziri@example.com", # must be unique and must not be null
	"password": "mypassword", # must not be null
	"phone": ""
}

u2data = {
	"userId": "", # must be unique
	"firstName": "Chinagoro", # must not be null
	"lastName": "Obioha", # must not be null
	"email": "chinagoro@example.com", # must be unique and must not be null
	"password": "mypassword", # must not be null
	"phone": "08012345678"
}

bad_email_and_errors = [
	{"email": "", "error": {'field': 'email', 'message': 'Email is required'}, 'status_code': 422},
	{"email": "ontopchime@gmail", "error": {'field': 'email', 'message': 'Invalid email'}, 'status_code': 422},
	{"email": "ontopchime@gmail.com", "error": {'field': 'email', 'message': 'User with email exits'}, 'status_code': 422}
]

def register_user(data):
    reg_url = f"{request.base_url}/auth/register"
    # data.update({'user'})
    return client.post(reg_url, data=data)
    # return User.query.filter_by(data['email']).first()

def test_reg_user_without_phone():
    resp = register_user(client, u1data)
    assert resp['status'] == "success"
    assert resp.status_code == 201
    assert resp['message'] == "Registration successful"
    assert resp['data']['accessToken']

    u = User.query.filter_by(email=u1data['email']).first()
    assert isinstance(u, User)
    assert u.userId

    # remove password & add id to get a match
    inp_password = u1data.pop('password')
    u1data.update({'userId': u.userId})

    assert resp['data']['user'] == u1data

    assert u.firstName == u1data['firstName']
    assert u.lastName == u1data['lastName']
    assert u.email == u1data['email']
    assert u.phone == u1data['phone']
    assert u.password and u.password != inp_password

    assert u.default_org


def test_reg_user_with_full_detail():
    resp = register_user(client, u1data)
    assert resp['status'] == "success"
    assert resp.status_code == 201
    assert resp['message'] == "Registration successful"
    assert resp['data']['accessToken']

    u1 = User.query.filter_by(phone=u1data['phone']).first()
    u2 = User.query.filter_by(email=u1data['email']).first()

    assert u1 == u2
    assert u1.default_org

# def test_reg_user_with_bad_emails():
#    for d in bad_emails_and_errors:
#	u3data = u2data.copy().update({'email': d['email']})
#	resp = register_user(client, u3data)
#	assert d['error'] in resp.json()['errors']
#	assert resp.status_code == d['status_code']

def test_reg_2_users_with_same_email():
    resp1 = register_user(client, u1data)
    assert resp1['status'] == "success"
    assert resp1.status_code == 201
    assert resp1['message'] == "Registration successful"

    u3data = u2data.copy()
    u3data.update({'email': u1data['email']})
    resp2 = register_user(client, u3data)
    
    assert resp1.status_code == 422
    assert {'field': 'email', 'message': 'User with email exits'} in resp2['errors']

# def test_reg_user_without_email():
#    u3data = u2data.copy().update({'email': ""})
#    resp = register_user(client, u3data)
#    assert resp.status_code == 422
#    assert {'field': 'email', 'message': 'Email is required} in resp['errors']

def test_reg_user_with_invalid_email():
    u3data = u2data.copy()
    u3data.update({'email': "ontopchimegmail.com"})
    resp = register_user(client, u3data)
    assert resp.status_code == 422
    assert {'field': 'email', 'message': 'Invalid email'} in resp['errors']

def test_reg_user_without_required_fields():
    for f in required_user_fiels:
        u3data = u1data.copy()
        u3data.update({f: ""})
        resp = register_user(client, u3data)
        assert resp.status_code == 422
        assert {'field': f, 'message': f"{f.title()} is required"} in resp['errors']


