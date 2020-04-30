import json

from app.models.route import Route
from app.models.robot import Robot
from app.models.robot_route import RobotRoute
from app.models.docking_station import DockingStation
from app.schemas.robot import RobotSchema
from app.tests.base import BaseTestCase

BASE_URL = 'http://127.0.0.1:5000/api/v1.0/robots'


class RobotAPITest(BaseTestCase):
    def setUp(self):
        self.docking_station = DockingStation.create(-74.0478, 12.4687)
        self.route = Route.create([[-75.10, 12.50], [-81.42, 10.92]])
        self.robot_schema = RobotSchema()
        self.robot = Robot.create(self.route.id, None)

    def tearDown(self):
        for robot in Robot.get_all():
            robot.delete()
        for docking_station in DockingStation.get_all():
            docking_station.delete()
        for route in Route.get_all():
            route.delete()
        for robot_route in RobotRoute.get_all():
            robot_route.delete()

    def test_get_robot(self):
        url = BASE_URL + '/{}'.format(self.robot.id)
        response = self.client.get(url)
        data = json.loads(response.get_data())
        expected_data = self.robot_schema.dump(self.robot)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, expected_data.data)

    def test_get_nonexistent_robot(self):
        url = BASE_URL + '/99'
        response = self.client.get(url)
        data = json.loads(response.get_data())

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data, {'error': 'Robot 99 could not be found'})

    def test_get_all_robots(self):
        Robot.create(None, self.docking_station.id)
        response = self.client.get(BASE_URL)
        data = json.loads(response.get_data())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 2)

    def test_put_robot(self):
        url = BASE_URL + '/{}'.format(self.robot.id)
        json_data = json.dumps({'docking_station_id': self.docking_station.id})
        response = self.client.put(url, data=json_data, content_type='application/json')
        data = json.loads(response.get_data())

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(data['id'])
        self.assertIsNotNone(data['modified_ts'])
        self.assertIsNone(data['route_id'])
        self.assertIsNotNone(data['docking_station_id'])

    def test_put_robot_with_invalid_args(self):
        url = BASE_URL + '/{}'.format(self.robot.id)
        json_data = json.dumps({'tacocat_id': 33})
        response = self.client.put(url, data=json_data, content_type='application/json')
        data = json.loads(response.get_data())

        expected_msgs = {'errors': 'Robot must have route_id or docking_station_id'}

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data, expected_msgs)

    def test_put_nonexistent_robot(self):
        url = BASE_URL + '/99'
        json_data = json.dumps({'docking_station_id': self.docking_station.id})
        response = self.client.put(url, data=json_data, content_type='application/json')
        data = json.loads(response.get_data())

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data, {'error': 'Robot 99 could not be found'})

    def test_delete_robot(self):
        url = BASE_URL + '/{}'.format(self.robot.id)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 204)

    def test_delete_nonexistent_robot(self):
        url = BASE_URL + '/99'
        response = self.client.delete(url)
        data = json.loads(response.get_data())

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data, {'error': 'Robot 99 could not be found'})

    def test_create_robot(self):
        json_data = json.dumps({'docking_station_id': self.docking_station.id})
        response = self.client.post(BASE_URL, data=json_data, content_type='application/json')
        data = json.loads(response.get_data())

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(data['id'])
        self.assertIsNotNone(data['docking_station_id'])

    def test_create_robot_with_additional_args(self):
        json_data = json.dumps({'route_id': self.route.id, 'tacocat': 33})
        response = self.client.post(BASE_URL, data=json_data, content_type='application/json')
        data = json.loads(response.get_data())

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(data['id'])
        self.assertIsNotNone(data['route_id'])

    def test_create_robot_with_invalid_args(self):
        json_data = json.dumps({'racecar': []})
        response = self.client.post(BASE_URL, data=json_data, content_type='application/json')
        data = json.loads(response.get_data())

        self.assertEqual(response.status_code, 400)
        expected_msgs = {'errors': 'Robot must have route_id or docking_station_id'}
        self.assertEqual(data, expected_msgs)
