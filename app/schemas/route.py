from marshmallow import Schema, fields


class RouteSchema(Schema):
    id = fields.Int(dump_only=True)
    points = fields.List(fields.List(fields.Float, equal=2, load_only=True), required=True)
    created_ts = fields.DateTime(dump_only=True)
    modified_ts = fields.DateTime(dump_only=True)
