import sqlalchemy as sa
from datetime import datetime

from app import db
from app.models import InvalidArguments
from app.models.base import Base
from app.models.drone_route import DroneRoute
from app.models.route import Route


class Drone(db.Model, Base):
    __tablename__ = 'drone'

    __table_args__ = (
        sa.CheckConstraint('NOT(station_id IS NULL AND route_id IS NULL)'),
        sa.CheckConstraint('NOT(station_id IS NOT NULL AND route_id IS NOT NULL)'),
    )

    id = db.Column(db.Integer, primary_key=True)
    route_id = db.Column(db.Integer, db.ForeignKey('route.id'))
    station_id = db.Column(db.Integer, db.ForeignKey('station.id'))
    created_ts = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    modified_ts = db.Column(db.DateTime, onupdate=datetime.utcnow)
    drone_routes = db.relationship('DroneRoute', backref='drone_route', lazy=True)

    def __repr__(self):
        return "<Drone {} route_id={} station_id={}>".format(self.id, self.route_id, self.station_id)

    @classmethod
    def create(cls, route_id, station_id):
        if (route_id and station_id) or (not route_id and not station_id):
            raise InvalidArguments('Drone must have route_id or station_id')

        drone = Drone(route_id=route_id, station_id=station_id)
        db.session.add(drone)
        db.session.commit()
        if route_id:
            DroneRoute.create(drone.id, drone.route_id, drone.created_ts)

        return drone


    def _is_ts_within_drone_route_range(self, drone_route, ts):
        if drone_route.end_ts:
            if drone_route.start_ts <= ts <= drone_route.end_ts:
                return True
        else:
            # drone route has not finished
            if drone_route.start_ts <= ts:
                return True
        return False

    def _does_ts_range_overlap_drone_route(self, drone_route, start_ts, end_ts):
        if self._is_ts_within_drone_route_range(drone_route, start_ts):
            return True
        elif self._is_ts_within_drone_route_range(drone_route, end_ts):
            return True
        elif (start_ts <= drone_route.start_ts):
            if drone_route.end_ts and (end_ts >= drone_route.end_ts):
                return True
            elif not drone_route.end_ts and (drone_route.start_ts < end_ts):
                return True

        return False

    def delete(self):
        for drone_route in self.drone_routes:
            drone_route.delete()

        db.session.delete(self)
        db.session.commit()

    def update(self, route_id=None, station_id=None):
        if (route_id and station_id) or (not route_id and not station_id):
            raise InvalidArguments('Drone must have route_id or station_id')

        if route_id and (route_id == self.route_id):
            return self

        self._end_current_route()
        if route_id:
            self.route_id = route_id
            self.station_id = None
            DroneRoute.create(self.id, route_id, datetime.utcnow())
        elif station_id:
            self.station_id = station_id
            self.route_id = None

        db.session.add(self)
        db.session.commit()

    def current_drone_route(self):
        for drone_route in self.drone_routes:
            if not drone_route.end_ts:
                return drone_route

        return None

    def find_route_by_ts(self, ts):
        for drone_route in self.drone_routes:
            if self._is_ts_within_drone_route_range(drone_route, ts):
                return [Route.get(drone_route.route_id)]

        return []

    def find_routes_by_ts_range(self, start_ts=None, end_ts=None):
        start_ts = start_ts or datetime(1970, 1, 1)
        end_ts = end_ts or datetime.utcnow()

        routes = []
        for drone_route in self.drone_routes:
            if self._does_ts_range_overlap_drone_route(drone_route, start_ts, end_ts):
                routes.append(Route.get(drone_route.route_id))

        return routes

    def _end_current_route(self):
        if not self.route_id:
            return
        # end current drone_route
        drone_route = self.current_drone_route()
        drone_route.update(datetime.utcnow())
