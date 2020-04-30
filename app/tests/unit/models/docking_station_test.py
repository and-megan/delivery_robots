from geoalchemy2.elements import WKBElement

from app.models.robot import Robot
from app.models.robot_route import RobotRoute
from app.models.route import Route
from app.models.docking_station import DockingStation
from app.tests.base import BaseTestCase


class DockingStationTest(BaseTestCase):
    def tearDown(self):
        for robot in Robot.get_all():
            robot.delete()
        for docking_station in DockingStation.get_all():
            docking_station.delete()
        for route in Route.get_all():
            route.delete()
        for robot_route in RobotRoute.get_all():
            robot_route.delete()

    def test_create_docking_station(self):
        longitude = -90.200391
        latitude = -1.163508
        docking_station = DockingStation.create(longitude, latitude)

        db_docking_station = DockingStation.get(docking_station.id)
        self.assertIsNotNone(db_docking_station)
        self.assertEqual(db_docking_station.longitude, longitude)
        self.assertEqual(db_docking_station.latitude, latitude)
        self.assertIsNotNone(db_docking_station.created_ts)
        self.assertIsNone(db_docking_station.modified_ts)
        self.assertEqual((type(db_docking_station.geo)), WKBElement)

    def test_create_docking_station_with_incomplete_args(self):
        longitude = -91.200391
        docking_station = None
        with self.assertRaises(TypeError):
            docking_station = DockingStation.create(longitude)

        self.assertIsNone(docking_station)

    def test_get_docking_station(self):
        docking_station = DockingStation.create(-90.3370, -1.3625)
        docking_station_id = docking_station.id

        db_docking_station = DockingStation.get(docking_station_id)
        self.assertEqual(db_docking_station.id, docking_station_id)

    def test_get_nonexistent_docking_station(self):
        docking_station = DockingStation.get(100)
        self.assertIsNone(docking_station)

    def test_update_docking_station(self):
        original_latitude = -1.362549
        original_longitude = -90.337096
        original_docking_station = DockingStation.create(original_longitude, original_latitude)
        original_geo = original_docking_station.geo
        self.assertIsNone(original_docking_station.modified_ts)

        new_latitude = -1.054879
        updated_docking_station = original_docking_station.update(latitude=new_latitude)
        self.assertEqual(updated_docking_station.latitude, new_latitude)
        self.assertEqual(updated_docking_station.longitude, original_longitude)
        self.assertNotEqual(updated_docking_station.geo, original_geo)
        self.assertIsNotNone(updated_docking_station.modified_ts)

    def test_delete_docking_station(self):
        docking_station = DockingStation.create(-90.350, -1.133)
        docking_station_id = docking_station.id
        self.assertIsNotNone(docking_station)

        docking_station.delete()
        db_docking_station = DockingStation.get(docking_station_id)
        self.assertIsNone(db_docking_station)

    def test_get_all_in_radius(self):
        target_longitude = -75.4980
        target_latitude = 12.1897

        for points in self._get_waypoints():
            DockingStation.create(points[0], points[1])

        radius500 = DockingStation.get_all_in_radius(target_longitude, target_latitude, 500)
        radius450 = DockingStation.get_all_in_radius(target_longitude, target_latitude, 450)
        radius300 = DockingStation.get_all_in_radius(target_longitude, target_latitude, 300)
        radius290 = DockingStation.get_all_in_radius(target_longitude, target_latitude, 290)
        radius100 = DockingStation.get_all_in_radius(target_longitude, target_latitude, 100)
        radius0 = DockingStation.get_all_in_radius(target_longitude, target_latitude, 0)

        self.assertEqual(len(radius500), 8)
        self.assertEqual(len(radius450), 7)
        self.assertEqual(len(radius300), 6)
        self.assertEqual(len(radius290), 3)
        self.assertEqual(len(radius100), 1)
        self.assertEqual(len(radius0), 0)

    def test_get_all_in_route_radius(self):
        route = self._create_route()
        DockingStation.create(-85.0341, -43.1330)
        DockingStation.create(-86.7480, -22.6748)
        DockingStation.create(-73.7402, -22.4719)
        DockingStation.create(-114.6972, 11.3507)

        radius0 = DockingStation.get_all_in_route_radius(route, 0)
        radius400 = DockingStation.get_all_in_route_radius(route, 400)
        radius700 = DockingStation.get_all_in_route_radius(route, 700)
        radius2500 = DockingStation.get_all_in_route_radius(route, 2500)

        self.assertEqual(len(radius0), 1)  # should return docking_station on route
        self.assertEqual(len(radius400), 2)
        self.assertEqual(len(radius700), 3)
        self.assertEqual(len(radius2500), 4)

    def _get_waypoints(self):
        return [
            [-79.8706, 14.6045],  # 293.44 NM
            [-80.4199, 10.9196],  # 299.18 NM
            [-74.0478, 12.4687],  # 86.63 NM
            [-79.3212, 15.4960],  # 298.23 NM
            [-83.5620, 11.4800],  # 475.43 NM
            [-79.6508, 10.4662],  # 265.28 NM
            [-80.3000, 10.4662],  # 300.81 NM
            [-79.3000, 11.4662],  # 227.45 NM
            [79.3000, -11.4662]  # 9319.52 NM

        ]

    def _create_route(self):
        points = [
            [-79.6289, -10.7901],
            [-77.0800, -16.5098],
            [-73.7402, -22.4719],
            [-75.4980, -30.6757],
            [-81.9140, - 36.9147]
        ]

        return Route.create(points)
