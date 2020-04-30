import sqlalchemy as sa
from datetime import datetime, timezone

from app import db
from app.models import InvalidArguments
from app.models.base import Base
from app.models.robot_route import RobotRoute
from app.models.route import Route


class Robot(db.Model, Base):
    __tablename__ = 'robot'

    __table_args__ = (
        sa.CheckConstraint('NOT(docking_station_id IS NULL AND route_id IS NULL)'),
        sa.CheckConstraint('NOT(docking_station_id IS NOT NULL AND route_id IS NOT NULL)'),
    )

    id = db.Column(db.Integer, primary_key=True)
    route_id = db.Column(db.Integer, db.ForeignKey('route.id'))
    docking_station_id = db.Column(db.Integer, db.ForeignKey('docking_station.id'))
    created_ts = db.Column(db.DateTime, nullable=False, default=datetime.now(tz=timezone.utc))
    modified_ts = db.Column(db.DateTime, onupdate=datetime.now(tz=timezone.utc))
    robot_routes = db.relationship('RobotRoute', backref='robot_route', lazy=True)

    def __repr__(self):
        return "<Robot {} route_id={} docking_station_id={}>".format(self.id, self.route_id, self.docking_station_id)

    @classmethod
    def create(cls, route_id, docking_station_id):
        if (route_id and docking_station_id) or (not route_id and not docking_station_id):
            raise InvalidArguments('Robot must have route_id or docking_station_id')

        robot = Robot(route_id=route_id, docking_station_id=docking_station_id)
        db.session.add(robot)
        db.session.commit()
        if route_id:
            RobotRoute.create(robot.id, robot.route_id, robot.created_ts)

        return robot


    def _is_ts_within_robot_route_range(self, robot_route, ts):
        if robot_route.end_ts:
            if robot_route.start_ts <= ts <= robot_route.end_ts:
                return True
        else:
            # robot route has not finished
            if robot_route.start_ts <= ts:
                return True
        return False

    def _does_ts_range_overlap_robot_route(self, robot_route, start_ts, end_ts):
        if self._is_ts_within_robot_route_range(robot_route, start_ts):
            return True
        elif self._is_ts_within_robot_route_range(robot_route, end_ts):
            return True
        elif (start_ts <= robot_route.start_ts):
            if robot_route.end_ts and (end_ts >= robot_route.end_ts):
                return True
            elif not robot_route.end_ts and (robot_route.start_ts < end_ts):
                return True

        return False

    def delete(self):
        for robot_route in self.robot_routes:
            robot_route.delete()

        db.session.delete(self)
        db.session.commit()

    def update(self, route_id=None, docking_station_id=None):
        if (route_id and docking_station_id) or (not route_id and not docking_station_id):
            raise InvalidArguments('Robot must have route_id or docking_station_id')

        if route_id and (route_id == self.route_id):
            return self

        self._end_current_route()
        if route_id:
            self.route_id = route_id
            self.docking_station_id = None
            RobotRoute.create(self.id, route_id, datetime.now(tz=timezone.utc))
        elif docking_station_id:
            self.docking_station_id = docking_station_id
            self.route_id = None

        db.session.add(self)
        db.session.commit()

    def current_robot_route(self):
        for robot_route in self.robot_routes:
            if not robot_route.end_ts:
                return robot_route

        return None

    def find_route_by_ts(self, ts):
        for robot_route in self.robot_routes:
            if self._is_ts_within_robot_route_range(robot_route, ts):
                return [Route.get(robot_route.route_id)]

        return []

    def find_routes_by_ts_range(self, start_ts=None, end_ts=None):
        start_ts = start_ts or datetime(1970, 1, 1)
        end_ts = end_ts or datetime.now(tz=timezone.utc)

        routes = []
        for robot_route in self.robot_routes:
            if self._does_ts_range_overlap_robot_route(robot_route, start_ts, end_ts):
                routes.append(Route.get(robot_route.route_id))

        return routes

    def _end_current_route(self):
        if not self.route_id:
            return
        # end current robot_route
        robot_route = self.current_robot_route()
        robot_route.update(datetime.now(tz=timezone.utc))
