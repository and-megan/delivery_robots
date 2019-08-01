from geoalchemy2.elements import WKBElement

from app.models.drone import Drone
from app.models.drone_route import DroneRoute
from app.models.route import Route
from app.models.station import Station
from app.tests.base import BaseTestCase


class RouteTest(BaseTestCase):
    def setUp(self):
        self.points = [[-11.3432, -14.1030], [-10.01, -11.43], [-75.0492, -40.3222]]

    def tearDown(self):
        for drone in Drone.get_all():
            drone.delete()
        for station in Station.get_all():
            station.delete()
        for route in Route.get_all():
            route.delete()
        for drone_route in DroneRoute.get_all():
            drone_route.delete()

    def test_create_route(self):
        route = Route.create(self.points)
        db_route = Route.get(route.id)

        self.assertIsNotNone(db_route.path)
        self.assertEqual(type(db_route.path), WKBElement)
        self.assertIsNotNone(db_route.created_ts)
        self.assertIsNone(db_route.modified_ts)
        self.assertEqual(db_route.drones, [])

    def test_get_route(self):
        route = Route.create(self.points)
        route_id = route.id
        db_route = Route.get(route_id)

        self.assertEqual(db_route.id, route_id)

    def test_get_nonexistent_route(self):
        route = Route.get(100)
        self.assertIsNone(route)

    def test_update_route(self):
        route = Route.create(self.points)
        original_path = route.path
        original_points = route.points
        self.assertIsNone(route.modified_ts)

        new_points = [[-1.3223, -14.3221], [-1.0531, -15.3221]]
        route.update(new_points)
        self.assertNotEqual(route.path, original_path)
        self.assertNotEqual(route.points, original_points)
        self.assertIsNotNone(route.modified_ts)

    def test_delete_route(self):
        route = Route.create(self.points)
        route_id = route.id
        self.assertIsNotNone(route)

        route.delete()
        db_route = Route.get(route_id)
        self.assertIsNone(db_route)
