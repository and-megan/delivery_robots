from marshmallow import Schema, fields


class DroneSchema(Schema):
    id = fields.Int(dump_only=True)
    route_id = fields.Int()
    station_id = fields.Int()
    created_ts = fields.DateTime(dump_only=True)
    modified_ts = fields.DateTime(dump_only=True)
