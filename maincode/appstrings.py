""""""


class lcl:
    user = "user"
    name = "name"
    users = "users"
    error = "error"
    token = "token"
    user_id = "user_id"
    creator = "creator"
    dynamic = "dynamic"
    default = "default"
    testing = "testing"
    message = "message"
    datetime = "datetime"
    production = "production"
    production = "production"
    development = "development"
    description = "description"
    organisations = "organisations"


class ccl:
    USER = "User"
    SUCCESS = "Success"
    ORGANISATION = "Organisation"


class ucl:
    WAT = "WAT"
    SECRET_KEY = "SECRET_KEY"
    COMMIT_HASH = "COMMIT_HASH"
    DATABASE_URL = "DATABASE_URL"
    PRODUCTION_ENV = "PRODUCTION_ENV"
    APP_SECRET_KEY = "APP_SECRET_KEY"
    JWT_SECRET_KEY = "JWT_SECRET_KEY"
    HNG11_T2_DEV_POSTGRESQL_DATABASE_URI = "HNG11_T2_DEV_POSTGRESQL_DATABASE_URI"
    HNG11_T2_PROD_POSTGRESQL_DATABASE_URI = "HNG11_T2_PROD_POSTGRESQL_DATABASE_URI"
    HNG11_T2_TEST_POSTGRESQL_DATABASE_URI = "HNG11_T2_TEST_POSTGRESQL_DATABASE_URI"


# def is_intent_str(s):
#     return not s.startswith('__') and not callable(s)


# # ccl DICT
# ccl_dict = {k: v for k, v in ccl.__dict__.items() if is_intent_str(k)}

# # lcl DICT
# lcl_dict = {k: v for k, v in lcl.__dict__.items() if is_intent_str(k)}

# # ucl DICT
# ucl_dict = {k: v for k, v in ucl.__dict__.items() if is_intent_str(k)}
