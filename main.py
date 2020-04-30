from app import app
from app import db
from app.models.robot import Robot
from app.models.robot_route import RobotRoute
from app.models.route import Route
from app.models.docking_station import DockingStation


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Robot': Robot, 'RobotRoute': RobotRoute, 'Route': Route, 'DockingStation': DockingStation}
