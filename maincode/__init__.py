
import os
import sentry_sdk
from flask_smorest import Api
from flask_admin import Admin
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, g, current_app
from flask_jwt_extended import JWTManager
from flask_admin.contrib.sqla import ModelView
from sentry_sdk.integrations.flask import FlaskIntegration


from maincode import config
from .appstrings import lcl, ucl


api = Api()
db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()
login_manager = LoginManager()
admin = Admin(template_mode='bootstrap4')


def create_app(config_type=None):

    app = Flask(__name__)
    migrate = Migrate(app, db)

    if config_type is None:
        config_type = lcl.development

    app.config.from_object(config.config_classes[config_type])
    config.config_classes[config_type].init_app(app)
    config.BaseConfig.CONFIG_TYPE = config_type

    sentry_sdk.init(
        dsn=f"{os.environ.get(ucl.SENTRY_DSN_FOR_HNG)}",
        integrations=[FlaskIntegration()],
        traces_sample_rate=1.0
    )

    app.config['API_SPEC_OPTIONS'] = {
        'security': [{"bearerAuth": []}],
        'components': {
            "securitySchemes":
                {
                    "bearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT"
                    }
                }
        }
    }

    with app.app_context():
        g.db = db
        g.db.init_app(app)
        migrate.init_app(app, db)
        api.init_app(current_app)
        jwt.init_app(current_app)
        admin.init_app(current_app)
        bcrypt.init_app(current_app)
        login_manager.init_app(current_app)

    # Import MAIN app blueprints
    from maincode.mainapp.routes import mainapp
    from maincode.mainapi.routes import mainapi

    # Import API blueprints
    from maincode.mainapi.accounts import sm_accounts

    # Register MAIN app blueprints
    app.register_blueprint(mainapp)
    app.register_blueprint(mainapi)

    # Register API blueprints
    with app.app_context():
        api.register_blueprint(sm_accounts)

    return app


class ViewOnly(ModelView):
    can_create = False
    can_edit = False
    can_delete = False


class UserAdminView(ViewOnly):
    column_hide_backrefs = False
    column_list = (
        'userId', 'firstName', 'lastName', 'email',
        'organisations', 'organisations_created',
        'phone', 'password', '_accessTokens',
    )


class OrganisationAdminView(ViewOnly):
    pass


from maincode.mainapp.model import User, Organisation


admin.add_view(UserAdminView(User, db.session))
admin.add_view(OrganisationAdminView(Organisation, db.session))
