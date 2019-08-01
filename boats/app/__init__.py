from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app.resources.drone import DroneAPI, DroneListAPI
from app.resources.route import RouteAPI, RouteListAPI
from app.resources.station import StationAPI, StationListAPI

api = Api(app)
api.add_resource(DroneAPI, '/api/v1.0/drones/<int:id>', endpoint='drone')
api.add_resource(DroneListAPI, '/api/v1.0/drones', endpoint='drones')
api.add_resource(RouteAPI, '/api/v1.0/routes/<int:id>', endpoint='route')
api.add_resource(RouteListAPI, '/api/v1.0/routes', endpoint='routes')
api.add_resource(StationAPI, '/api/v1.0/stations/<int:id>', endpoint='station')
api.add_resource(StationListAPI, '/api/v1.0/stations', endpoint='stations')
