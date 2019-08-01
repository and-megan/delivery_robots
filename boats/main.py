from app import app
from app import db
from app.models.drone import Drone
from app.models.drone_route import DroneRoute
from app.models.route import Route
from app.models.station import Station


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Drone': Drone, 'DroneRoute': DroneRoute, 'Route': Route, 'Station': Station}
