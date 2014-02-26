from core.tests.base import RealizeTest
from core.database.manager import DBManager
from core.manager import ExecutionContext

class DatabaseTest(RealizeTest):

    def test_manager(self):
        manager = DBManager()