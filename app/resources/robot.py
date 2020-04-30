from flask import request

from app.models.robot import Robot
from app.resources.base import BaseAPI, BaseListAPI
from app.schemas.robot import RobotSchema


class RobotAPI(BaseAPI):
    def __init__(self):
        self.model_schema = RobotSchema()
        self.model_update_schema = RobotSchema()
        self.model_cls = Robot
        super(RobotAPI, self).__init__()

    @staticmethod
    def _parse_request_json(data):
        return {
            'route_id': request.json.get('route_id'),
            'docking_station_id': request.json.get('docking_station_id')
        }


class RobotListAPI(BaseListAPI):
    def __init__(self):
        self.model_schema = RobotSchema()
        self.models_schema = RobotSchema(many=True)
        self.model_cls = Robot
        super(RobotListAPI, self).__init__()

    @staticmethod
    def _parse_schema_data(schema_data):
        route_id = schema_data.data.get('route_id')
        docking_station_id = schema_data.data.get('docking_station_id')

        return [route_id, docking_station_id]