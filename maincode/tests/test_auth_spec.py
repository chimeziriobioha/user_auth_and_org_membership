from maincode import db, create_app, jwt
from maincode.mainapp import utils as au
from maincode.mainapp.model import User, Organisation


unique_user_fields = ["userId", "email"]

required_user_fields = ["userId", "firstName", "lastName", "email", "password"]

u1data = {
	# "userId": "", # must be unique
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


def register_user(app, client, data):
    return client.post(f"http://localhost:5000/auth/register", json=data)


def test_reg_user_without_phone(app, client):
    with app.app_context():
        with app.test_request_context():
            with app.test_client() as client:
                resp = register_user(app, client, u1data)
                resp_d = resp.json
                # print(resp.data)
                # print(resp.text)
                # print(resp.json)
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

                assert u.firstName == u1data['firstName']
                assert u.lastName == u1data['lastName']
                assert u.email == u1data['email']
                assert u.phone == u1data['phone']
                assert u.password and u.password != inp_password

                assert u.default_org


def test_reg_user_with_full_detail(app, client):
    with app.app_context():
        with app.test_request_context():
            with app.test_client() as client:
                resp = register_user(app, client, u1data)
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
                resp1 = register_user(app, client, u1data)
                resp1_d = resp1.json
                assert resp1.status_code == 201
                assert resp1_d['status'] == "success"
                assert resp1_d['message'] == "Registration successful"

                u3data = u2data.copy()
                u3data.update({'email': u1data['email']})
                resp2 = register_user(app, client, u3data)
                
                assert resp2.status_code == 422
                print(resp2.json)
                assert {'field': 'email', 'message': 'User with email exits'} in resp2.json['errors']


def test_reg_user_with_invalid_email(app, client):
    with app.app_context():
        with app.test_request_context():
            with app.test_client() as client:
                u3data = u2data.copy()
                u3data.update({'email': "ontopchimegmail.com"})
                resp = register_user(app, client, u3data)
                assert resp.status_code == 422
                assert {'field': 'email', 'message': 'Invalid email'} in resp.json['errors']


def test_reg_user_without_required_fields(app, client):
    with app.app_context():
        with app.test_request_context():
            with app.test_client() as client:
                for f in required_user_fields:
                    u3data = u1data.copy()
                    u3data.update({f: ""})
                    resp = register_user(app, client, u3data)
                    assert resp.status_code == 422
                    assert {'field': f, 'message': f"{f.title()} is required"} in resp.json['errors']


