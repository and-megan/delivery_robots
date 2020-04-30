import unittest
from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

from config import TestConfig
from app.resources.robot import RobotAPI, RobotListAPI
from app.resources.route import RouteAPI, RouteListAPI
from app.resources.docking_station import DockingStationAPI, DockingStationListAPI


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
        cls.api.add_resource(RobotAPI, '/api/v1.0/robots/<int:id>', endpoint='robot')
        cls.api.add_resource(RobotListAPI, '/api/v1.0/robots', endpoint='robots')
        cls.api.add_resource(RouteAPI, '/api/v1.0/routes/<int:id>', endpoint='route')
        cls.api.add_resource(RouteListAPI, '/api/v1.0/routes', endpoint='routes')
        cls.api.add_resource(DockingStationAPI, '/api/v1.0/docking_stations/<int:id>', endpoint='docking_station')
        cls.api.add_resource(DockingStationListAPI, '/api/v1.0/docking_stations', endpoint='docking_stations')
