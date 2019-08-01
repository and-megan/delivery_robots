import json

from app.models.route import Route
from app.models.drone import Drone
from app.models.drone_route import DroneRoute
from app.models.station import Station
from app.schemas.drone import DroneSchema
from app.tests.base import BaseTestCase

BASE_URL = 'http://127.0.0.1:5000/api/v1.0/drones'


class DroneAPITest(BaseTestCase):
    def setUp(self):
        self.station = Station.create(-74.0478, 12.4687)
        self.route = Route.create([[-75.10, 12.50], [-81.42, 10.92]])
        self.drone_schema = DroneSchema()
        self.drone = Drone.create(self.route.id, None)

    def tearDown(self):
        for drone in Drone.get_all():
            drone.delete()
        for station in Station.get_all():
            station.delete()
        for route in Route.get_all():
            route.delete()
        for drone_route in DroneRoute.get_all():
            drone_route.delete()

    def test_get_drone(self):
        url = BASE_URL + '/{}'.format(self.drone.id)
        response = self.client.get(url)
        data = json.loads(response.get_data())
        expected_data = self.drone_schema.dump(self.drone)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, expected_data.data)

    def test_get_nonexistent_drone(self):
        url = BASE_URL + '/99'
        response = self.client.get(url)
        data = json.loads(response.get_data())

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data, {'error': 'Drone 99 could not be found'})

    def test_get_all_drones(self):
        Drone.create(None, self.station.id)
        response = self.client.get(BASE_URL)
        data = json.loads(response.get_data())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 2)

    def test_put_drone(self):
        url = BASE_URL + '/{}'.format(self.drone.id)
        json_data = json.dumps({'station_id': self.station.id})
        response = self.client.put(url, data=json_data, content_type='application/json')
        data = json.loads(response.get_data())

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(data['id'])
        self.assertIsNotNone(data['modified_ts'])
        self.assertIsNone(data['route_id'])
        self.assertIsNotNone(data['station_id'])

    def test_put_drone_with_invalid_args(self):
        url = BASE_URL + '/{}'.format(self.drone.id)
        json_data = json.dumps({'tacocat_id': 33})
        response = self.client.put(url, data=json_data, content_type='application/json')
        data = json.loads(response.get_data())

        expected_msgs = {'errors': 'Drone must have route_id or station_id'}

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data, expected_msgs)

    def test_put_nonexistent_drone(self):
        url = BASE_URL + '/99'
        json_data = json.dumps({'station_id': self.station.id})
        response = self.client.put(url, data=json_data, content_type='application/json')
        data = json.loads(response.get_data())

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data, {'error': 'Drone 99 could not be found'})

    def test_delete_drone(self):
        url = BASE_URL + '/{}'.format(self.drone.id)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 204)

    def test_delete_nonexistent_drone(self):
        url = BASE_URL + '/99'
        response = self.client.delete(url)
        data = json.loads(response.get_data())

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data, {'error': 'Drone 99 could not be found'})

    def test_create_drone(self):
        json_data = json.dumps({'station_id': self.station.id})
        response = self.client.post(BASE_URL, data=json_data, content_type='application/json')
        data = json.loads(response.get_data())

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(data['id'])
        self.assertIsNotNone(data['station_id'])

    def test_create_drone_with_additional_args(self):
        json_data = json.dumps({'route_id': self.route.id, 'tacocat': 33})
        response = self.client.post(BASE_URL, data=json_data, content_type='application/json')
        data = json.loads(response.get_data())

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(data['id'])
        self.assertIsNotNone(data['route_id'])

    def test_create_drone_with_invalid_args(self):
        json_data = json.dumps({'racecar': []})
        response = self.client.post(BASE_URL, data=json_data, content_type='application/json')
        data = json.loads(response.get_data())

        self.assertEqual(response.status_code, 400)
        expected_msgs = {'errors': 'Drone must have route_id or station_id'}
        self.assertEqual(data, expected_msgs)
