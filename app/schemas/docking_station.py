from marshmallow import Schema, fields


class DockingStationSchema(Schema):
    id = fields.Int(dump_only=True)
    longitude = fields.Float(required=True)
    latitude = fields.Float(required=True)
    created_ts = fields.DateTime(dump_only=True)
    modified_ts = fields.DateTime(dump_only=True)

class DockingStationUpdateSchema(Schema):
    latitude = fields.Float()
    longitude = fields.Float()
