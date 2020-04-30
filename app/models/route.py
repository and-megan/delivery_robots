import datetime
from datetime import timezone
import json
import sqlalchemy as sa
from geoalchemy2 import Geometry

from app import db
from app.common.helpers import validate_point, validate_and_extract_datetimes
from app.models import NotFound
from app.models.base import Base


class Route(db.Model, Base):
    __tablename__ = 'route'

    id = db.Column(db.Integer, primary_key=True)
    points = db.Column(db.Text, nullable=False)
    path = db.Column(Geometry(geometry_type='LINESTRING', srid=4326), nullable=False)
    created_ts = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now(tz=timezone.utc))
    modified_ts = db.Column(db.DateTime, onupdate=datetime.datetime.now(tz=timezone.utc))
    robots = db.relationship('Robot', backref='robot', lazy=True)

    def __repr__(self):
        return "<Route {} points={}>".format(self.id, self.points)

    @classmethod
    def create(cls, points):
        geo_points = cls._calculate_geo_points(points)
        path = sa.func.ST_MakeLine(geo_points)

        route = Route(path=path, points=json.dumps(geo_points))
        db.session.add(route)
        db.session.commit()

        return route

    @classmethod
    def get_all(cls, query_string=None):
        from app.models.robot import Robot

        query_string = json.loads(query_string) if query_string else {}
        if not query_string.get('robot_id'):
            return cls.query.all()

        robot = Robot.get(query_string.get('robot_id'))
        if not robot:
            raise NotFound({'resource_name': 'Robot', 'id': query_string.get('robot_id')})

        target_dt, start_dt, end_dt = validate_and_extract_datetimes(query_string)

        if target_dt:
            robot.find_route_by_ts(target_dt)

        return robot.find_routes_by_ts_range(start_ts=start_dt, end_ts=end_dt)

    def update(self, points):
        geo_points = self._calculate_geo_points(points)
        new_path = sa.func.ST_MakeLine(geo_points)
        self.path = new_path
        self.points = geo_points

        db.session.add(self)
        db.session.commit()

    @staticmethod
    def _calculate_geo_points(points):
        geos = []
        # points = [[longitude, latitude], [longitude, latitude]]
        for point in points:
            longitude = point[0]
            latitude = point[1]
            validate_point(longitude, latitude)
            geos.append('POINT({} {})'.format(longitude, latitude))

        return geos
