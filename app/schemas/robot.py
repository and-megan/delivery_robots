from marshmallow import Schema, fields


class RobotSchema(Schema):
    id = fields.Int(dump_only=True)
    route_id = fields.Int()
    docking_station_id = fields.Int()
    created_ts = fields.DateTime(dump_only=True)
    modified_ts = fields.DateTime(dump_only=True)
