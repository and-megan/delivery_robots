from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app.resources.robot import RobotAPI, RobotListAPI
from app.resources.route import RouteAPI, RouteListAPI
from app.resources.docking_station import DockingStationAPI, DockingStationListAPI

api = Api(app)
api.add_resource(RobotAPI, '/api/v1.0/robots/<int:id>', endpoint='robot')
api.add_resource(RobotListAPI, '/api/v1.0/robots', endpoint='robots')
api.add_resource(RouteAPI, '/api/v1.0/routes/<int:id>', endpoint='route')
api.add_resource(RouteListAPI, '/api/v1.0/routes', endpoint='routes')
api.add_resource(DockingStationAPI, '/api/v1.0/docking_stations/<int:id>', endpoint='docking_station')
api.add_resource(DockingStationListAPI, '/api/v1.0/docking_stations', endpoint='docking_stations')
