from flask import request

from app.models.drone import Drone
from app.resources.base import BaseAPI, BaseListAPI
from app.schemas.drone import DroneSchema


class DroneAPI(BaseAPI):
    def __init__(self):
        self.model_schema = DroneSchema()
        self.model_update_schema = DroneSchema()
        self.model_cls = Drone
        super(DroneAPI, self).__init__()

    @staticmethod
    def _parse_request_json(data):
        return {
            'route_id': request.json.get('route_id'),
            'station_id': request.json.get('station_id')
        }


class DroneListAPI(BaseListAPI):
    def __init__(self):
        self.model_schema = DroneSchema()
        self.models_schema = DroneSchema(many=True)
        self.model_cls = Drone
        super(DroneListAPI, self).__init__()

    @staticmethod
    def _parse_schema_data(schema_data):
        route_id = schema_data.data.get('route_id')
        station_id = schema_data.data.get('station_id')

        return [route_id, station_id]