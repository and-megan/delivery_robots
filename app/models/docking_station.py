import datetime
from datetime import timezone
import json
from sqlalchemy import func
from geoalchemy2 import Geometry

from app import db
from app.common.helpers import validate_point
from app.models.base import Base
from app.models.route import Route


class DockingStation(db.Model, Base):
    __tablename__ = 'docking_station'

    id = db.Column(db.Integer, primary_key=True)
    longitude = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    geo = db.Column(Geometry(geometry_type='POINT', srid=4326))
    created_ts = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now(tz=timezone.utc))
    modified_ts = db.Column(db.DateTime, onupdate=datetime.datetime.now(tz=timezone.utc))
    robots = db.relationship('Robot', backref='docking_station', lazy=True)

    def __repr__(self):
        return "<DockingStation {} (long:{}, lat:{})>".format(self.id, self.longitude, self.latitude)

    @classmethod
    def create(cls, longitude, latitude):
        validate_point(longitude, latitude)
        geo = 'POINT({} {})'.format(longitude, latitude)
        docking_station = DockingStation(longitude=longitude, latitude=latitude, geo=geo)
        db.session.add(docking_station)
        db.session.commit()

        return docking_station

    @classmethod
    def get_all(cls, query_string=None):
        query_string = json.loads(query_string) if query_string else {}
        if not query_string.get('radius'):
            return cls.query.all()

        if query_string.get('route_id'):
            route = Route.get(query_string['route_id'])
            return cls.get_all_in_route_radius(route, query_string['radius'])

        return cls.get_all_in_radius(query_string['target_longitude'], query_string['target_latitude'], query_string['radius'])

    @classmethod
    def get_all_in_route_radius(cls, route, radius):
        # convert nautical miles to meters
        m_radius = radius * 1852
        return cls.query.filter(func.ST_Distance_Sphere(cls.geo, route.path) <= m_radius).all()

    @classmethod
    def get_all_in_radius(cls, longitude, latitude, radius):
        # convert nautical miles to meters
        m_radius = radius * 1852
        target_point = 'POINT({} {})'.format(longitude, latitude)
        return cls.query.filter(func.ST_Distance_Sphere(cls.geo, target_point) <= m_radius).all()

    def update(self, **kwargs):
        if kwargs.get('longitude'):
            self.longitude = kwargs.get('longitude')
        if kwargs.get('latitude'):
            self.latitude = kwargs.get('latitude')

        validate_point(self.longitude, self.latitude)
        geo = 'POINT({} {})'.format(self.longitude, self.latitude)
        self.geo = geo

        db.session.add(self)
        db.session.commit()

        return self
