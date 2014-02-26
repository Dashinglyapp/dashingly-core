from flask.ext.testing import TestCase

from app import create_test_app, db

class RealizeTest(TestCase):

    def create_app(self):
        app = create_test_app()
        db.init_app(app)
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()