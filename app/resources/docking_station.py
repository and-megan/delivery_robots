from flask import request

from app.models.docking_station import DockingStation
from app.resources.base import BaseAPI, BaseListAPI
from app.schemas.docking_station import DockingStationSchema, DockingStationUpdateSchema


class DockingStationAPI(BaseAPI):
    def __init__(self):
        self.model_schema = DockingStationSchema()
        self.model_update_schema = DockingStationUpdateSchema()
        self.model_cls = DockingStation
        super(DockingStationAPI, self).__init__()

    @staticmethod
    def _parse_request_json(data):
        longitude = request.json.get('longitude')
        latitude = request.json.get('latitude')
        return {
            'longitude': longitude,
            'latitude': latitude
        }

class DockingStationListAPI(BaseListAPI):
    def __init__(self):
        self.model_schema = DockingStationSchema()
        self.models_schema = DockingStationSchema(many=True)
        self.model_cls = DockingStation
        super(DockingStationListAPI, self).__init__()

    @staticmethod
    def _parse_schema_data(schema_data):
        latitude = schema_data.data['latitude']
        longitude = schema_data.data['longitude']

        return [longitude, latitude]
