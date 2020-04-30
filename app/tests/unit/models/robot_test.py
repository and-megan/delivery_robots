from unittest import mock
from datetime import datetime

from app.tests.base import BaseTestCase
from app.models import InvalidArguments
from app.models.robot import Robot
from app.models.robot_route import RobotRoute
from app.models.route import Route
from app.models.docking_station import DockingStation


class RobotTest(BaseTestCase):
    def setUp(self):
        self.route = Route.create([[-79, 14], [-78, 15]])
        self.docking_station = DockingStation.create(-80, 14)

    def tearDown(self):
        for robot in Robot.get_all():
            robot.delete()
        for docking_station in DockingStation.get_all():
            docking_station.delete()
        for route in Route.get_all():
            route.delete()
        for robot_route in RobotRoute.get_all():
            robot_route.delete()

    @mock.patch('app.models.robot_route.RobotRoute.create')
    def test_create_robot_with_route(self, create):
        robot = Robot.create(self.route.id, None)
        db_robot = Robot.get(robot.id)

        create.assert_called_with(robot.id, self.route.id, robot.created_ts)
        self.assertIsNotNone(db_robot)
        self.assertIsNotNone(db_robot.created_ts)
        self.assertIsNone(db_robot.modified_ts)
        self.assertIsNone(db_robot.docking_station_id)
        self.assertEqual(db_robot.route_id, self.route.id)

    @mock.patch('app.models.robot_route.RobotRoute.create')
    def test_create_robot_with_docking_station(self, create):
        robot = Robot.create(None, self.docking_station.id)
        db_robot = Robot.get(robot.id)

        create.assert_not_called()
        self.assertIsNotNone(db_robot)
        self.assertIsNotNone(db_robot.created_ts)
        self.assertIsNone(db_robot.modified_ts)
        self.assertIsNone(db_robot.route_id)
        self.assertEqual(db_robot.docking_station_id, self.docking_station.id)

    def test_create_robot_with_route_and_docking_station(self):
        robot = None
        with self.assertRaises(InvalidArguments):
            robot = Robot.create(self.route.id, self.docking_station.id)

        self.assertIsNone(robot)

    def test_get_robot(self):
        robot = Robot.create(None, self.docking_station.id)
        db_robot = Robot.get(robot.id)

        self.assertEqual(db_robot.id, robot.id)

    def test_get_nonexistent_robot(self):
        robot = Robot.get(100)
        self.assertIsNone(robot)

    def test_delete_robot(self):
        robot = Robot.create(None, self.docking_station.id)
        robot.delete()
        robot_db = Robot.get(robot.id)

        self.assertIsNone(robot_db)

    def test_update_robot_on_route_to_docking_station(self):
        robot = Robot.create(self.route.id, None)
        old_robot_route = robot.current_robot_route()

        robot.update(docking_station_id=self.docking_station.id)
        updated_robot_route = robot.current_robot_route()

        self.assertIsNone(robot.route_id)
        self.assertEqual(robot.docking_station_id, self.docking_station.id)
        self.assertIsNotNone(old_robot_route.end_ts)
        self.assertIsNone(updated_robot_route)
        self.assertTrue(robot in self.docking_station.robots)

    def test_update_robot_to_same_route(self):
        robot = Robot.create(self.route.id, None)
        old_robot_route = robot.current_robot_route()

        robot.update(route_id=self.route.id)
        updated_robot_route = robot.current_robot_route()

        self.assertEqual(old_robot_route, updated_robot_route)
        self.assertIsNone(robot.docking_station_id)

    def test_update_robot_on_route_to_new_route(self):
        robot = Robot.create(self.route.id, None)
        old_robot_route = robot.current_robot_route()

        new_route = Route.create([[-11, -11], [9, 19], [10, 15]])
        robot.update(route_id=new_route.id)
        updated_robot_route = robot.current_robot_route()

        self.assertEqual(robot.route_id, new_route.id)
        self.assertNotEqual(old_robot_route, updated_robot_route)
        self.assertIsNotNone(old_robot_route.end_ts)
        self.assertIsNone(updated_robot_route.end_ts)
        self.assertTrue(robot in new_route.robots)
        self.assertIsNone(robot.docking_station_id)

    def test_update_robot_at_docking_station_to_new_docking_station(self):
        robot = Robot.create(None, self.docking_station.id)
        new_docking_station = DockingStation.create(-44, -11)
        robot.update(docking_station_id=new_docking_station.id)

        self.assertEqual(robot.docking_station_id, new_docking_station.id)
        self.assertIsNone(robot.route_id)

    def test_update_robot_at_docking_station_to_route(self):
        robot = Robot.create(None, self.docking_station.id)
        current_robot_route = robot.current_robot_route()

        robot.update(route_id=self.route.id)
        updated_robot_route = robot.current_robot_route()

        self.assertEqual(robot.route_id, self.route.id)
        self.assertIsNone(robot.docking_station_id)
        self.assertIsNone(current_robot_route)
        self.assertIsNotNone(updated_robot_route)
        self.assertIsNone(updated_robot_route.end_ts)

    def test_find_route_by_ts_when_ts_in_middle(self):
        data = self._create_robot_routes()
        robot = data['robot']

        # check ts falls in middle of robot route 1
        robot_route_1_ts = datetime(2018, 2, 2)
        robot_route_1_ts_result = robot.find_route_by_ts(robot_route_1_ts)[-1]

        self.assertEqual(robot_route_1_ts_result.id, data['robot_route_1_route_id'])

    def test_find_route_by_ts_when_ts_on_edge(self):
        data = self._create_robot_routes()
        robot = data['robot']

        # check ts falls on edge of robot route
        robot_route_2_ts = datetime(2018, 5, 27)
        robot_route_2_ts_result = robot.find_route_by_ts(robot_route_2_ts)[-1]

        self.assertEqual(robot_route_2_ts_result.id, data['robot_route_2_route_id'])

    def test_find_route_by_ts_with_no_match(self):
        data = self._create_robot_routes()
        robot = data['robot']

        # return no route if ts not in the middle robot route
        no_route_ts = datetime(2018, 4, 4)
        no_route_ts_result = robot.find_route_by_ts(no_route_ts)

        self.assertEqual(no_route_ts_result, [])

    def test_find_route_by_ts_on_incomplete_route(self):
        data = self._create_robot_routes()
        robot = data['robot']

        # return a result when the robot route is incomplete
        robot_route_5_ts = datetime(2019, 7, 1)
        robot_route_5_ts_result = robot.find_route_by_ts(robot_route_5_ts)[-1]

        self.assertEqual(robot_route_5_ts_result.id, data['robot_route_5_route_id'])

    def test_find_routes_by_ts_range(self):
        data = self._create_robot_routes()
        robot = data['robot']
        start_ts = datetime(2018, 10, 12)
        end_ts = datetime(2019, 5, 9)

        result = sorted([route.id for route in robot.find_routes_by_ts_range(start_ts=start_ts, end_ts=end_ts)])
        expected = [data['robot_route_3_route_id'], data['robot_route_4_route_id']]
        self.assertEqual(result, expected)

    def test_find_route_by_ts_range_on_incomplete_route(self):
        data = self._create_robot_routes()
        robot = data['robot']
        start_ts = datetime(2019, 5, 12)
        end_ts = datetime(2019, 7, 4)

        result = [route.id for route in robot.find_routes_by_ts_range(start_ts=start_ts, end_ts=end_ts)]
        self.assertEqual(result, [data['robot_route_5_route_id']])

    def test_find_route_by_ts_range_without_results(self):
        data = self._create_robot_routes()
        robot = data['robot']
        start_ts = datetime(2018, 3, 5)
        end_ts = datetime(2018, 4, 5)

        result = robot.find_routes_by_ts_range(start_ts=start_ts, end_ts=end_ts)
        self.assertEqual(result, [])

    def test_find_route_by_ts_range_without_start_ts(self):
        data = self._create_robot_routes()
        robot = data['robot']
        end_ts = datetime(2018, 12, 12)

        routes = robot.find_routes_by_ts_range(end_ts=end_ts)
        result = sorted([route.id for route in routes])

        expected_route_ids = sorted(
            [data['robot_route_1_route_id'], data['robot_route_2_route_id'], data['robot_route_3_route_id']])
        self.assertEqual(result, expected_route_ids)

    def test_find_route_by_ts_range_without_end_ts(self):
        data = self._create_robot_routes()
        robot = data['robot']
        start_ts = datetime(2019, 2, 5)

        routes = robot.find_routes_by_ts_range(start_ts=start_ts)
        result = sorted([route.id for route in routes])
        expected_route_ids = sorted([data['robot_route_4_route_id'], data['robot_route_5_route_id']])
        self.assertEqual(result, expected_route_ids)

    def _create_robot_routes(self):
        robot = Robot.create(self.route.id, None)
        robot.robot_routes[-1].delete()

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

        robot_route_1 = RobotRoute.create(robot.id, self.route.id, t1)
        robot_route_1.update(t2)

        robot_route_2 = RobotRoute.create(robot.id, route_1.id, t3)
        robot_route_2.update(t4)

        robot_route_3 = RobotRoute.create(robot.id, route_2.id, t5)
        robot_route_3.update(t6)

        robot_route_4 = RobotRoute.create(robot.id, route_3.id, t7)
        robot_route_4.update(t8)

        robot_route_5 = RobotRoute.create(robot.id, route_4.id, t9)

        return {
            'robot': robot,
            'robot_route_1_route_id': robot_route_1.route_id,
            'robot_route_2_route_id': robot_route_2.route_id,
            'robot_route_3_route_id': robot_route_3.route_id,
            'robot_route_4_route_id': robot_route_4.route_id,
            'robot_route_5_route_id': robot_route_5.route_id
        }
