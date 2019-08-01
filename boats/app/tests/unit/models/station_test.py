from geoalchemy2.elements import WKBElement

from app.models.drone import Drone
from app.models.drone_route import DroneRoute
from app.models.route import Route
from app.models.station import Station
from app.tests.base import BaseTestCase


class StationTest(BaseTestCase):
    def tearDown(self):
        for drone in Drone.get_all():
            drone.delete()
        for station in Station.get_all():
            station.delete()
        for route in Route.get_all():
            route.delete()
        for drone_route in DroneRoute.get_all():
            drone_route.delete()

    def test_create_station(self):
        longitude = -90.200391
        latitude = -1.163508
        station = Station.create(longitude, latitude)

        db_station = Station.get(station.id)
        self.assertIsNotNone(db_station)
        self.assertEqual(db_station.longitude, longitude)
        self.assertEqual(db_station.latitude, latitude)
        self.assertIsNotNone(db_station.created_ts)
        self.assertIsNone(db_station.modified_ts)
        self.assertEqual((type(db_station.geo)), WKBElement)

    def test_create_station_with_incomplete_args(self):
        longitude = -91.200391
        station = None
        with self.assertRaises(TypeError):
            station = Station.create(longitude)

        self.assertIsNone(station)

    def test_get_station(self):
        station = Station.create(-90.3370, -1.3625)
        station_id = station.id

        db_station = Station.get(station_id)
        self.assertEqual(db_station.id, station_id)

    def test_get_nonexistent_station(self):
        station = Station.get(100)
        self.assertIsNone(station)

    def test_update_station(self):
        original_latitude = -1.362549
        original_longitude = -90.337096
        original_station = Station.create(original_longitude, original_latitude)
        original_geo = original_station.geo
        self.assertIsNone(original_station.modified_ts)

        new_latitude = -1.054879
        updated_station = original_station.update(latitude=new_latitude)
        self.assertEqual(updated_station.latitude, new_latitude)
        self.assertEqual(updated_station.longitude, original_longitude)
        self.assertNotEqual(updated_station.geo, original_geo)
        self.assertIsNotNone(updated_station.modified_ts)

    def test_delete_station(self):
        station = Station.create(-90.350, -1.133)
        station_id = station.id
        self.assertIsNotNone(station)

        station.delete()
        db_station = Station.get(station_id)
        self.assertIsNone(db_station)

    def test_get_all_in_radius(self):
        target_longitude = -75.4980
        target_latitude = 12.1897

        for points in self._get_waypoints():
            Station.create(points[0], points[1])

        radius500 = Station.get_all_in_radius(target_longitude, target_latitude, 500)
        radius450 = Station.get_all_in_radius(target_longitude, target_latitude, 450)
        radius300 = Station.get_all_in_radius(target_longitude, target_latitude, 300)
        radius290 = Station.get_all_in_radius(target_longitude, target_latitude, 290)
        radius100 = Station.get_all_in_radius(target_longitude, target_latitude, 100)
        radius0 = Station.get_all_in_radius(target_longitude, target_latitude, 0)

        self.assertEqual(len(radius500), 8)
        self.assertEqual(len(radius450), 7)
        self.assertEqual(len(radius300), 6)
        self.assertEqual(len(radius290), 3)
        self.assertEqual(len(radius100), 1)
        self.assertEqual(len(radius0), 0)

    def test_get_all_in_route_radius(self):
        route = self._create_route()
        Station.create(-85.0341, -43.1330)
        Station.create(-86.7480, -22.6748)
        Station.create(-73.7402, -22.4719)
        Station.create(-114.6972, 11.3507)

        radius0 = Station.get_all_in_route_radius(route, 0)
        radius400 = Station.get_all_in_route_radius(route, 400)
        radius700 = Station.get_all_in_route_radius(route, 700)
        radius2500 = Station.get_all_in_route_radius(route, 2500)

        self.assertEqual(len(radius0), 1)  # should return station on route
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
