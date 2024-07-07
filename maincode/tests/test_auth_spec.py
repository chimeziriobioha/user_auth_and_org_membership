from datetime import datetime, timezone
from maincode.mainapp import utils as au
from flask_jwt_extended import decode_token
from maincode.mainapp.model import User, Organisation


unique_user_fields = ["userId", "email"]

required_user_fields = ["firstName", "lastName", "email", "password"]

u1data = {
	# "userId": "", # must be unique
	"firstName": "Chimeziri", # must not be null
	"lastName": "Obioha", # must not be null
	"email": "chimeziri@example.com", # must be unique and must not be null
	"password": "mypassword", # must not be null
	"phone": ""
}

u2data = {
	# "userId": "", # must be unique
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


def register_user(client, data):
    return client.post("http://localhost:5000/auth/register", json=data)


def login_user(client, data):
    return client.post("http://localhost:5000/auth/login", json=data)


def test_reg_user_without_phone(app, client):
    with app.app_context():
        with app.test_request_context():
            with app.test_client() as client:
                resp = register_user(client, u1data)
                resp_d = resp.json
                # check request response
                assert resp.status_code == 201
                assert resp_d['status'] == "success"
                assert resp_d['message'] == "Registration successful"
                assert resp_d['data']['accessToken']

                u = User.query.filter_by(email=u1data['email']).first()
                assert isinstance(u, User)
                assert u.userId

                # remove password & add id to get a match
                inp_password = u1data.pop('password')
                u1data.update({'userId': u.userId})

                assert resp_d['data']['user'] == u1data

                # check user details
                assert u.firstName == u1data['firstName']
                assert u.lastName == u1data['lastName']
                assert u.email == u1data['email']
                assert u.phone == u1data['phone']
                assert u.password and u.password != inp_password

                del u1data['userId']  # To avoind later issues

                # check default organisation
                assert u.default_org

                # check token correctness
                access_token = resp_d['data']['accessToken']
                decoded_token = decode_token(access_token)
                assert decoded_token['sub'] == u.id

                # check token expiry
                exp_dt = datetime.fromtimestamp(decoded_token['exp'], timezone.utc)
                assert (exp_dt - au.aware_utcnow()).days == 29  # days minus fews seconds


def test_reg_user_with_full_detail(app, client):
    with app.app_context():
        with app.test_request_context():
            with app.test_client() as client:
                resp = register_user(client, u1data)
                resp_d = resp.json
                assert resp.status_code == 201
                assert resp_d['status'] == "success"
                assert resp_d['message'] == "Registration successful"
                assert resp_d['data']['accessToken']

                u1 = User.query.filter_by(phone=u1data['phone']).first()
                u2 = User.query.filter_by(email=u1data['email']).first()

                assert u1 == u2
                assert u1.default_org


def test_reg_2_users_with_same_email(app, client):
    with app.app_context():
        with app.test_request_context():
            with app.test_client() as client:
                resp1 = register_user(client, u1data)
                resp1_d = resp1.json
                assert resp1.status_code == 201
                assert resp1_d['status'] == "success"
                assert resp1_d['message'] == "Registration successful"

                u3data = u2data.copy()
                u3data.update({'email': u1data['email']})
                resp2 = register_user(client, u3data)
                
                assert resp2.status_code == 422
                assert {'field': 'email', 'message': 'User with email exists'} == resp2.json['errors'][0]


def test_reg_user_with_invalid_email(app, client):
    with app.app_context():
        with app.test_request_context():
            with app.test_client() as client:
                u3data = u2data.copy()
                u3data.update({'email': "ontopchimegmail.com"})
                resp = register_user(client, u3data)
                assert resp.status_code == 422
                assert {'field': 'email', 'message': 'Invalid email'} == resp.json['errors'][0]


def test_reg_user_without_required_fields(app, client):
    with app.app_context():
        with app.test_request_context():
            with app.test_client() as client:
                for f in required_user_fields:
                    u3data = u1data.copy()
                    u3data.update({f: ""})
                    resp = register_user(client, u3data)
                    assert resp.status_code == 422
                    print(resp.json['errors'])
                    assert {'field': f, 'message': f"{f.title()} is required"} == resp.json['errors'][0]


def test_login(app, client):
    with app.app_context():
        with app.test_request_context():
            with app.test_client() as client:
                register_user(client, u1data)
                u = User.query.filter_by(email=u1data['email']).first()
                assert u

                resp = login_user(client, {'email': u.email, 'password': u1data['password']})
                resp_d = resp.json

                # check request response
                assert resp.status_code == 200
                assert resp_d['status'] == "success"
                assert resp_d['message'] == "Login successful"
                assert resp_d['data']['accessToken']

                # remove password & add id to get a match
                _ = u1data.pop('password')
                u1data.update({'userId': u.userId})

                assert resp_d['data']['user'] == u1data
                
                # check token correctness
                access_token = resp_d['data']['accessToken']
                decoded_token = decode_token(access_token)
                assert decoded_token['sub'] == u.id

                # check token expiry
                exp_dt = datetime.fromtimestamp(decoded_token['exp'], timezone.utc)
                assert (exp_dt - au.aware_utcnow()).days == 29  # days minus fews seconds


# def test_organisations_and_access(app, client):
#     with app.app_context():
#         with app.test_request_context():
#             with app.test_client() as client:
#                 register_user(client, u1data)
#                 register_user(client, u2data)

#                 u1 = User.query.filter_by(email=u1data['email']).first()
#                 u2 = User.query.filter_by(email=u2data['email']).first()
#                 assert u1 and u2

#                 assert u1.defaul_org not in u2.organisations
#                 assert u2.defaul_org not in u1.organisations




