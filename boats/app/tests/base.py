import unittest
from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

from config import TestConfig
from app.resources.drone import DroneAPI, DroneListAPI
from app.resources.route import RouteAPI, RouteListAPI
from app.resources.station import StationAPI, StationListAPI


def clean_db(db):
    for table in reversed(db.metadata.sorted_tables):
        db.session.execute(table.delete())


class BaseTestCase(unittest.TestCase):
    db = None

    @classmethod
    def setUpClass(cls):
        super(BaseTestCase, cls).setUpClass()
        cls.app = Flask(__name__)
        cls.app.config.from_object(TestConfig)
        cls.db = SQLAlchemy(cls.app)
        cls.register_api(cls.app)
        cls.client = cls.app.test_client()
        cls.db.app = cls.app
        cls.db.create_all()

    @classmethod
    def tearDownClass(cls):
        cls.db.drop_all()
        super(BaseTestCase, cls).tearDownClass()

    def setUp(self):
        super(BaseTestCase, self).setUp()
        self.app_context = self.app.app_context()
        self.app_context.push()
        clean_db(self.db)

    def tearDown(self):
        self.db.session.rollback()
        self.app_context.pop()
        super(BaseTestCase, self).tearDown()

    @classmethod
    def register_api(cls, app):
        cls.api = Api(app)
        cls.api.add_resource(DroneAPI, '/api/v1.0/drones/<int:id>', endpoint='drone')
        cls.api.add_resource(DroneListAPI, '/api/v1.0/drones', endpoint='drones')
        cls.api.add_resource(RouteAPI, '/api/v1.0/routes/<int:id>', endpoint='route')
        cls.api.add_resource(RouteListAPI, '/api/v1.0/routes', endpoint='routes')
        cls.api.add_resource(StationAPI, '/api/v1.0/stations/<int:id>', endpoint='station')
        cls.api.add_resource(StationListAPI, '/api/v1.0/stations', endpoint='stations')
