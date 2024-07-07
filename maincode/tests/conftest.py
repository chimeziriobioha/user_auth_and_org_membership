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