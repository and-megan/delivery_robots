from flask import request

from app.models.station import Station
from app.resources.base import BaseAPI, BaseListAPI
from app.schemas.station import StationSchema, StationUpdateSchema


class StationAPI(BaseAPI):
    def __init__(self):
        self.model_schema = StationSchema()
        self.model_update_schema = StationUpdateSchema()
        self.model_cls = Station
        super(StationAPI, self).__init__()

    @staticmethod
    def _parse_request_json(data):
        longitude = request.json.get('longitude')
        latitude = request.json.get('latitude')
        return {
            'longitude': longitude,
            'latitude': latitude
        }

class StationListAPI(BaseListAPI):
    def __init__(self):
        self.model_schema = StationSchema()
        self.models_schema = StationSchema(many=True)
        self.model_cls = Station
        super(StationListAPI, self).__init__()

    @staticmethod
    def _parse_schema_data(schema_data):
        latitude = schema_data.data['latitude']
        longitude = schema_data.data['longitude']

        return [longitude, latitude]
