import datetime
import json

from app.models.robot import Robot
from app.models.route import Route
from app.models.robot_route import RobotRoute
from app.models.docking_station import DockingStation
from app.schemas.route import RouteSchema
from app.tests.base import BaseTestCase

BASE_URL = 'http://127.0.0.1:5000/api/v1.0/routes'


class RouteAPITest(BaseTestCase):
    def setUp(self):
        self.route = Route.create([[-74.0478, 12.4687], [-80.4199, 10.9196]])
        self.route2 = Route.create([[-75.0478, 12.4687], [-81.4199, 10.9196]])
        self.route_schema = RouteSchema()

    def tearDown(self):
        for robot in Robot.get_all():
            robot.delete()
        for docking_station in DockingStation.get_all():
            docking_station.delete()
        for route in Route.get_all():
            route.delete()
        for robot_route in RobotRoute.get_all():
            robot_route.delete()

    def test_get_route(self):
        url = BASE_URL + '/{}'.format(self.route.id)
        response = self.client.get(url)
        data = json.loads(response.get_data())
        expected_data = self.route_schema.dump(self.route)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, expected_data.data)

    def test_get_nonexistent_docking_station(self):
        url = BASE_URL + '/99'
        response = self.client.get(url)
        data = json.loads(response.get_data())

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data, {'error': 'Route 99 could not be found'})

    def test_get_all_routes(self):
        response = self.client.get(BASE_URL)
        data = json.loads(response.get_data())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 2)

    def test_get_all_routes_with_target_ts(self):
        dt = datetime.datetime(2018, 1, 1).timestamp()
        robot = Robot.create(self.route.id, None)
        json_data = json.dumps({'target_ts': dt, 'robot_id': robot.id})
        response = self.client.get(BASE_URL, query_string=json_data)
        data = json.loads(response.get_data())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 1)

    def test_get_all_routes_with_invalid_target_ts(self):
        dt = 'abc'
        robot = Robot.create(self.route.id, None)
        json_data = json.dumps({'target_ts': dt, 'robot_id': robot.id})
        response = self.client.get(BASE_URL, query_string=json_data)
        data = json.loads(response.get_data())

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data, {'errors': 'timestamp arguments must be UTC timestamps'})

    def test_get_all_routes_with_nonexistent_robot_id(self):
        robot_id = 99
        dt = datetime.datetime(2018, 1, 1).timestamp()
        json_data = json.dumps({'target_ts': dt, 'robot_id': robot_id})
        response = self.client.get(BASE_URL, query_string=json_data)
        data = json.loads(response.get_data())

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data, {'error': 'Robot 99 could not be found'})

    def test_get_all_routes_with_ts_range(self):
        robot = Robot.create(self.route.id, None)
        robot.update(self.route2.id, None)

        json_data = json.dumps({'robot_id': robot.id})
        response = self.client.get(BASE_URL, query_string=json_data)
        data = json.loads(response.get_data())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 2)

    def test_put_route(self):
        url = BASE_URL + '/{}'.format(self.route.id)
        json_data = json.dumps({'points': [[10, 10], [11, 11]]})
        response = self.client.put(url, data=json_data, content_type='application/json')
        data = json.loads(response.get_data())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['id'], self.route.id)
        self.assertIsNotNone(data['modified_ts'])

    def test_put_route_with_invalid_args(self):
        url = BASE_URL + '/{}'.format(self.route.id)
        json_data = json.dumps({'tacocat': [[10, 10], [11, 11]]})
        response = self.client.put(url, data=json_data, content_type='application/json')
        data = json.loads(response.get_data())

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data, {'errors': {'points': ['Missing data for required field.']}})

    def test_put_nonexistent_route(self):
        url = BASE_URL + '/99'
        json_data = json.dumps({'points': [[13, 13], [12, 12]]})
        response = self.client.put(url, data=json_data, content_type='application/json')
        data = json.loads(response.get_data())

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data, {'error': 'Route 99 could not be found'})

    def test_delete_route(self):
        url = BASE_URL + '/{}'.format(self.route.id)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 204)

    def test_delete_nonexistent_route(self):
        url = BASE_URL + '/99'
        response = self.client.delete(url)
        data = json.loads(response.get_data())

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data, {'error': 'Route 99 could not be found'})

    def test_create_route(self):
        json_data = json.dumps({'points': [[11, 11], [12, 12], [15, 15]]})
        response = self.client.post(BASE_URL, data=json_data, content_type='application/json')
        data = json.loads(response.get_data())

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(data['id'])

    def test_create_route_with_additional_args(self):
        json_data = json.dumps({'points': [[11, 11], [12, 12], [15, 15]]})
        response = self.client.post(BASE_URL, data=json_data, content_type='application/json')
        data = json.loads(response.get_data())

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(data['id'])

    def test_create_route_with_invalid_args(self):
        json_data = json.dumps({'racecar': []})
        response = self.client.post(BASE_URL, data=json_data, content_type='application/json')
        data = json.loads(response.get_data())

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data, {'errors': {'points': ['Missing data for required field.']}})

    def test_create_route_with_invalid_points(self):
        json_data = json.dumps({'points': [[10301, 13001], [12, 12]]})
        response = self.client.post(BASE_URL, data=json_data, content_type='application/json')
        data = json.loads(response.get_data())

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data, {'errors': 'Latitude and/or Longitude are out of range'})
