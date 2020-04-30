from app import db
from app.models.base import Base


class RobotRoute(db.Model, Base):
    __tablename__ = 'robot_route'

    id = db.Column(db.Integer, primary_key=True)
    route_id = db.Column(db.Integer, db.ForeignKey('route.id'), nullable=False)
    robot_id = db.Column(db.Integer, db.ForeignKey('robot.id'), nullable=False)
    start_ts = db.Column(db.DateTime, nullable=False)
    end_ts = db.Column(db.DateTime)

    def __repr__(self):
        return "<RobotRoute {} robot_id={} route_id={}>".format(self.id, self.route_id, self.robot_id)

    @classmethod
    def create(cls, robot_id, route_id, start_ts):
        robot_route = RobotRoute(robot_id=robot_id, route_id=route_id, start_ts=start_ts)
        db.session.add(robot_route)
        db.session.commit()

        return robot_route

    def update(self, end_ts):
        self.end_ts = end_ts
        db.session.add(self)
        db.session.commit()

        return self
