from marshmallow import Schema, fields


class UserSchema(Schema):
    userId = fields.Str(dump_only=True)
    firstName = fields.Str()
    lastName = fields.Str()
    email = fields.Str()
    password = fields.Str(load_only=True)
    phone = fields.Str()


class UserLoginSchema(Schema):
    email = fields.Str()
    password = fields.Str(load_only=True)


class AddUserToOrgSchema(Schema):
    userId = fields.Str()


class OrganisationSchema(Schema):
    orgId = fields.Str(dump_only=True)
    name = fields.Str()
    description = fields.Str()