from flask.ext.script import Command, Manager, Option
from realize import settings
import os
from app import app, initialize_app


class RunServer(Command):
    option_list = (
        Option('--port', '-p', dest='port'),
        Option('--hostname', '-hn', dest='host'),
    )

    def run(self, host="127.0.0.1", port=5000):
        app.run(debug=settings.DEBUG, host=host, port=port)
