from app import db
from app.models.base import Base


class DroneRoute(db.Model, Base):
    __tablename__ = 'drone_route'

    id = db.Column(db.Integer, primary_key=True)
    route_id = db.Column(db.Integer, db.ForeignKey('route.id'), nullable=False)
    drone_id = db.Column(db.Integer, db.ForeignKey('drone.id'), nullable=False)
    start_ts = db.Column(db.DateTime, nullable=False)
    end_ts = db.Column(db.DateTime)

    def __repr__(self):
        return "<DroneRoute {} drone_id={} route_id={}>".format(self.id, self.route_id, self.drone_id)

    @classmethod
    def create(cls, drone_id, route_id, start_ts):
        drone_route = DroneRoute(drone_id=drone_id, route_id=route_id, start_ts=start_ts)
        db.session.add(drone_route)
        db.session.commit()

        return drone_route

    def update(self, end_ts):
        self.end_ts = end_ts
        db.session.add(self)
        db.session.commit()

        return self
