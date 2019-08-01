from unittest import mock
from datetime import datetime

from app.tests.base import BaseTestCase
from app.models import InvalidArguments
from app.models.drone import Drone
from app.models.drone import DroneRoute
from app.models.route import Route
from app.models.station import Station


class DroneTest(BaseTestCase):
    def setUp(self):
        self.route = Route.create([[-79, 14], [-78, 15]])
        self.station = Station.create(-80, 14)

    def tearDown(self):
        for drone in Drone.get_all():
            drone.delete()
        for station in Station.get_all():
            station.delete()
        for route in Route.get_all():
            route.delete()
        for drone_route in DroneRoute.get_all():
            drone_route.delete()

    @mock.patch('app.models.drone_route.DroneRoute.create')
    def test_create_drone_with_route(self, create):
        drone = Drone.create(self.route.id, None)
        db_drone = Drone.get(drone.id)

        create.assert_called_with(drone.id, self.route.id, drone.created_ts)
        self.assertIsNotNone(db_drone)
        self.assertIsNotNone(db_drone.created_ts)
        self.assertIsNone(db_drone.modified_ts)
        self.assertIsNone(db_drone.station_id)
        self.assertEqual(db_drone.route_id, self.route.id)

    @mock.patch('app.models.drone_route.DroneRoute.create')
    def test_create_drone_with_station(self, create):
        drone = Drone.create(None, self.station.id)
        db_drone = Drone.get(drone.id)

        create.assert_not_called()
        self.assertIsNotNone(db_drone)
        self.assertIsNotNone(db_drone.created_ts)
        self.assertIsNone(db_drone.modified_ts)
        self.assertIsNone(db_drone.route_id)
        self.assertEqual(db_drone.station_id, self.station.id)

    def test_create_drone_with_route_and_station(self):
        drone = None
        with self.assertRaises(InvalidArguments):
            drone = Drone.create(self.route.id, self.station.id)

        self.assertIsNone(drone)

    def test_get_drone(self):
        drone = Drone.create(None, self.station.id)
        db_drone = Drone.get(drone.id)

        self.assertEqual(db_drone.id, drone.id)

    def test_get_nonexistent_drone(self):
        drone = Drone.get(100)
        self.assertIsNone(drone)

    def test_delete_drone(self):
        drone = Drone.create(None, self.station.id)
        drone.delete()
        drone_db = Drone.get(drone.id)

        self.assertIsNone(drone_db)

    def test_update_drone_on_route_to_station(self):
        drone = Drone.create(self.route.id, None)
        old_drone_route = drone.current_drone_route()

        drone.update(station_id=self.station.id)
        updated_drone_route = drone.current_drone_route()

        self.assertIsNone(drone.route_id)
        self.assertEqual(drone.station_id, self.station.id)
        self.assertIsNotNone(old_drone_route.end_ts)
        self.assertIsNone(updated_drone_route)
        self.assertTrue(drone in self.station.drones)

    def test_update_drone_to_same_route(self):
        drone = Drone.create(self.route.id, None)
        old_drone_route = drone.current_drone_route()

        drone.update(route_id=self.route.id)
        updated_drone_route = drone.current_drone_route()

        self.assertEqual(old_drone_route, updated_drone_route)
        self.assertIsNone(drone.station_id)

    def test_update_drone_on_route_to_new_route(self):
        drone = Drone.create(self.route.id, None)
        old_drone_route = drone.current_drone_route()

        new_route = Route.create([[-11, -11], [9, 19], [10, 15]])
        drone.update(route_id=new_route.id)
        updated_drone_route = drone.current_drone_route()

        self.assertEqual(drone.route_id, new_route.id)
        self.assertNotEqual(old_drone_route, updated_drone_route)
        self.assertIsNotNone(old_drone_route.end_ts)
        self.assertIsNone(updated_drone_route.end_ts)
        self.assertTrue(drone in new_route.drones)
        self.assertIsNone(drone.station_id)

    def test_update_drone_at_station_to_new_station(self):
        drone = Drone.create(None, self.station.id)
        new_station = Station.create(-44, -11)
        drone.update(station_id=new_station.id)

        self.assertEqual(drone.station_id, new_station.id)
        self.assertIsNone(drone.route_id)

    def test_update_drone_at_station_to_route(self):
        drone = Drone.create(None, self.station.id)
        current_drone_route = drone.current_drone_route()

        drone.update(route_id=self.route.id)
        updated_drone_route = drone.current_drone_route()

        self.assertEqual(drone.route_id, self.route.id)
        self.assertIsNone(drone.station_id)
        self.assertIsNone(current_drone_route)
        self.assertIsNotNone(updated_drone_route)
        self.assertIsNone(updated_drone_route.end_ts)

    def test_find_route_by_ts_when_ts_in_middle(self):
        data = self._create_drone_routes()
        drone = data['drone']

        # check ts falls in middle of drone route 1
        drone_route_1_ts = datetime(2018, 2, 2)
        drone_route_1_ts_result = drone.find_route_by_ts(drone_route_1_ts)[-1]

        self.assertEqual(drone_route_1_ts_result.id, data['drone_route_1_route_id'])

    def test_find_route_by_ts_when_ts_on_edge(self):
        data = self._create_drone_routes()
        drone = data['drone']

        # check ts falls on edge of drone route
        drone_route_2_ts = datetime(2018, 5, 27)
        drone_route_2_ts_result = drone.find_route_by_ts(drone_route_2_ts)[-1]

        self.assertEqual(drone_route_2_ts_result.id, data['drone_route_2_route_id'])

    def test_find_route_by_ts_with_no_match(self):
        data = self._create_drone_routes()
        drone = data['drone']

        # return no route if ts not in the middle drone route
        no_route_ts = datetime(2018, 4, 4)
        no_route_ts_result = drone.find_route_by_ts(no_route_ts)

        self.assertEqual(no_route_ts_result, [])

    def test_find_route_by_ts_on_incomplete_route(self):
        data = self._create_drone_routes()
        drone = data['drone']

        # return a result when the drone route is incomplete
        drone_route_5_ts = datetime(2019, 7, 1)
        drone_route_5_ts_result = drone.find_route_by_ts(drone_route_5_ts)[-1]

        self.assertEqual(drone_route_5_ts_result.id, data['drone_route_5_route_id'])

    def test_find_routes_by_ts_range(self):
        data = self._create_drone_routes()
        drone = data['drone']
        start_ts = datetime(2018, 10, 12)
        end_ts = datetime(2019, 5, 9)

        result = sorted([route.id for route in drone.find_routes_by_ts_range(start_ts=start_ts, end_ts=end_ts)])
        expected = [data['drone_route_3_route_id'], data['drone_route_4_route_id']]
        self.assertEqual(result, expected)

    def test_find_route_by_ts_range_on_incomplete_route(self):
        data = self._create_drone_routes()
        drone = data['drone']
        start_ts = datetime(2019, 5, 12)
        end_ts = datetime(2019, 7, 4)

        result = [route.id for route in drone.find_routes_by_ts_range(start_ts=start_ts, end_ts=end_ts)]
        self.assertEqual(result, [data['drone_route_5_route_id']])

    def test_find_route_by_ts_range_without_results(self):
        data = self._create_drone_routes()
        drone = data['drone']
        start_ts = datetime(2018, 3, 5)
        end_ts = datetime(2018, 4, 5)

        result = drone.find_routes_by_ts_range(start_ts=start_ts, end_ts=end_ts)
        self.assertEqual(result, [])

    def test_find_route_by_ts_range_without_start_ts(self):
        data = self._create_drone_routes()
        drone = data['drone']
        end_ts = datetime(2018, 12, 12)

        routes = drone.find_routes_by_ts_range(end_ts=end_ts)
        result = sorted([route.id for route in routes])

        expected_route_ids = sorted(
            [data['drone_route_1_route_id'], data['drone_route_2_route_id'], data['drone_route_3_route_id']])
        self.assertEqual(result, expected_route_ids)

    def test_find_route_by_ts_range_without_end_ts(self):
        data = self._create_drone_routes()
        drone = data['drone']
        start_ts = datetime(2019, 2, 5)

        routes = drone.find_routes_by_ts_range(start_ts=start_ts)
        result = sorted([route.id for route in routes])
        expected_route_ids = sorted([data['drone_route_4_route_id'], data['drone_route_5_route_id']])
        self.assertEqual(result, expected_route_ids)

    def _create_drone_routes(self):
        drone = Drone.create(self.route.id, None)
        drone.drone_routes[-1].delete()

        route_1 = Route.create([[-13, 15], [-13, 14]])
        route_2 = Route.create([[-11, 15], [-12, 14]])
        route_3 = Route.create([[-10, 15], [-11, 14]])
        route_4 = Route.create([[-10, 14], [-11, 14]])

        t1 = datetime(2018, 1, 1)
        t2 = datetime(2018, 3, 3)

        t3 = datetime(2018, 5, 27)
        t4 = datetime(2018, 10, 11)

        t5 = datetime(2018, 10, 12)
        t6 = datetime(2019, 1, 3)

        t7 = datetime(2019, 2, 2)
        t8 = datetime(2019, 5, 9)

        t9 = datetime(2019, 6, 6)

        drone_route_1 = DroneRoute.create(drone.id, self.route.id, t1)
        drone_route_1.update(t2)

        drone_route_2 = DroneRoute.create(drone.id, route_1.id, t3)
        drone_route_2.update(t4)

        drone_route_3 = DroneRoute.create(drone.id, route_2.id, t5)
        drone_route_3.update(t6)

        drone_route_4 = DroneRoute.create(drone.id, route_3.id, t7)
        drone_route_4.update(t8)

        drone_route_5 = DroneRoute.create(drone.id, route_4.id, t9)

        return {
            'drone': drone,
            'drone_route_1_route_id': drone_route_1.route_id,
            'drone_route_2_route_id': drone_route_2.route_id,
            'drone_route_3_route_id': drone_route_3.route_id,
            'drone_route_4_route_id': drone_route_4.route_id,
            'drone_route_5_route_id': drone_route_5.route_id
        }
