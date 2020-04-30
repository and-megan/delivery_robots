import json

from app.models.robot import Robot
from app.models.robot_route import RobotRoute
from app.models.route import Route
from app.models.docking_station import DockingStation
from app.schemas.docking_station import DockingStationSchema
from app.tests.base import BaseTestCase

BASE_URL = 'http://127.0.0.1:5000/api/v1.0/docking_stations'


class DockingStationAPITest(BaseTestCase):
    def setUp(self):
        self.docking_station = DockingStation.create(-74.0478, 12.4687)
        self.docking_station2 = DockingStation.create(-80.4199, 10.9196)
        self.docking_station3 = DockingStation.create(80.4199, -10.9196)
        self.docking_station_schema = DockingStationSchema()

    def tearDown(self):
        for robot in Robot.get_all():
            robot.delete()
        for docking_station in DockingStation.get_all():
            docking_station.delete()
        for route in Route.get_all():
            route.delete()
        for robot_route in RobotRoute.get_all():
            robot_route.delete()

    def test_get_docking_station(self):
        url = BASE_URL + '/{}'.format(self.docking_station.id)
        response = self.client.get(url)
        data = json.loads(response.get_data())
        expected_data = self.docking_station_schema.dump(self.docking_station)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, expected_data.data)

    def test_get_nonexistent_docking_station(self):
        url = BASE_URL + '/99'
        response = self.client.get(url)
        data = json.loads(response.get_data())

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data, {'error': 'DockingStation 99 could not be found'})

    def test_get_all_docking_stations(self):
        response = self.client.get(BASE_URL)
        data = json.loads(response.get_data())

        latitudes = sorted([docking_station['latitude'] for docking_station in data])
        expected_latitudes = sorted([-10.9196, 12.4687, 10.9196])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 3)
        self.assertEqual(latitudes, expected_latitudes)

    def test_get_all_docking_stations_in_radius(self):
        json_data = json.dumps({'radius': 500, 'target_latitude': 12.1897, 'target_longitude': -75.4980})
        response = self.client.get(BASE_URL, query_string=json_data)
        data = json.loads(response.get_data())

        self.assertEqual(len(data), 2)
        self.assertEqual(response.status_code, 200)

    def test_get_all_docking_stations_in_radius_of_route(self):
        route = Route.create([[-75.4980, 12.1897], [-75.4990, 12.1900]])
        json_data = json.dumps({'radius': 500, 'route_id': route.id})
        response = self.client.get(BASE_URL, query_string=json_data)
        data = json.loads(response.get_data())

        self.assertEqual(len(data), 2)
        self.assertEqual(response.status_code, 200)

    def test_put_docking_station(self):
        url = BASE_URL + '/{}'.format(self.docking_station.id)
        json_data = json.dumps({'longitude': 44})
        response = self.client.put(url, data=json_data, content_type='application/json')
        data = json.loads(response.get_data())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['longitude'], 44.0)
        self.assertEqual(data['latitude'], 12.4687)
        self.assertIsNotNone(data['modified_ts'])

    def test_put_nonexistent_docking_station(self):
        url = BASE_URL + '/99'
        json_data = json.dumps({'longitude': 44})
        response = self.client.put(url, data=json_data, content_type='application/json')
        data = json.loads(response.get_data())

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data, {'error': 'DockingStation 99 could not be found'})

    def test_delete_docking_station(self):
        url = BASE_URL + '/{}'.format(self.docking_station.id)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 204)

    def test_delete_nonexistent_docking_station(self):
        url = BASE_URL + '/99'
        response = self.client.delete(url)
        data = json.loads(response.get_data())

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data, {'error': 'DockingStation 99 could not be found'})

    def test_create_docking_station(self):
        json_data = json.dumps({'longitude': 30, 'latitude': 35})
        response = self.client.post(BASE_URL, data=json_data, content_type='application/json')
        data = json.loads(response.get_data())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['longitude'], 30)
        self.assertEqual(data['latitude'], 35)
        self.assertIsNotNone(data['id'])

    def test_create_docking_station_with_additional_args(self):
        json_data = json.dumps({'longitude': 30, 'latitude': 35, 'tacocat': 35})
        response = self.client.post(BASE_URL, data=json_data, content_type='application/json')
        data = json.loads(response.get_data())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['longitude'], 30)
        self.assertEqual(data['latitude'], 35)
        self.assertIsNotNone(data['id'])

    def test_create_docking_station_with_invalid_args(self):
        json_data = json.dumps({'longitude': 30})
        response = self.client.post(BASE_URL, data=json_data, content_type='application/json')
        data = json.loads(response.get_data())

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data, {'errors': {'latitude': ['Missing data for required field.']}})

    def test_create_docking_station_with_invalid_geography(self):
        json_data = json.dumps({'longitude': 30, 'latitude': 3500})
        response = self.client.post(BASE_URL, data=json_data, content_type='application/json')
        data = json.loads(response.get_data())

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data, {'errors': 'Latitude and/or Longitude are out of range'})
