from marshmallow import Schema, fields


from maincode.mainapp.model import User


def validate_email(value):
    return value and User.query.filter_by(email=value).first() is None


class UserSchema(Schema):
    userId = fields.Str(required=True)
    firstName = fields.Str(required=True)
    lastName = fields.Str(required=True)
    email = fields.Email(validate=validate_email)
    password = fields.Str(required=True, load_only=True)
    phone = fields.Str()


class OrganisationSchema(Schema):
    orgId = fields.Str(required=True, dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str(required=True)