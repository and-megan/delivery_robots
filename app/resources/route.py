from flask import request

from app.models.route import Route
from app.resources.base import BaseAPI, BaseListAPI
from app.schemas.route import RouteSchema


class RouteAPI(BaseAPI):
    def __init__(self):
        self.model_schema = RouteSchema()
        self.model_update_schema = RouteSchema()
        self.model_cls = Route
        super(RouteAPI, self).__init__()

    @staticmethod
    def _parse_request_json(data):
        return {'points': request.json['points']}


class RouteListAPI(BaseListAPI):
    def __init__(self):
        self.model_schema = RouteSchema()
        self.models_schema = RouteSchema(many=True)
        self.model_cls = Route
        super(RouteListAPI, self).__init__()

    @staticmethod
    def _parse_schema_data(schema_data):
        return [schema_data.data['points']]
