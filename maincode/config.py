import os
from datetime import datetime, timezone, timedelta

from maincode.appstrings import lcl, ccl, ucl


class BaseConfig:
    """
    GENEARL CONFIG ITEMS
    """
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SECRET_KEY = os.environ.get(ucl.APP_SECRET_KEY)
    CONFIG_TYPE = None  # updated in application factory
    COMMIT_HASH = datetime.now(tz=timezone.utc).isoformat()

    # API VARS
    API_VERSION = "v1"
    OPENAPI_URL_PREFIX = "/"
    OPENAPI_VERSION = "3.0.3"
    PROPAGATE_EXCEPTIONS = True
    OPENAPI_SWAGGER_UI_PATH = "/api/ui"
    API_TITLE = "HNG11 STAGE TWO TASK API"
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

    # JWT VARS
    JWT_SECREST_KEY = os.environ.get(ucl.JWT_SECRET_KEY)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=30)

    @staticmethod
    def init_app(app):
        pass


class TestingConfig(BaseConfig):
    DEBUG = True
    TESTING_ENV = True
    ROOT_DOMAIN = "http://localhost:5000"
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        ucl.HNG11_T2_TEST_POSTGRESQL_DATABASE_URI)


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    DEVELOPMENT_ENV = True
    ROOT_DOMAIN = "http://localhost:5000"
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        ucl.HNG11_T2_DEV_POSTGRESQL_DATABASE_URI)


class ProductionConfig(BaseConfig):
    ROOT_DOMAIN = ""
    PRODUCTION_ENV = True
    SQLALCHEMY_DATABASE_URI = \
        os.environ.get(ucl.DATABASE_URL) or os.environ.get(
            ucl.HNG11_T2_PROD_POSTGRESQL_DATABASE_URI)

    @classmethod
    def init_app(cls, app):
        BaseConfig.init_app(app)


config_classes = {
    lcl.testing: TestingConfig,
    lcl.default: DevelopmentConfig,
    lcl.production: ProductionConfig,
    lcl.development: DevelopmentConfig,
}
