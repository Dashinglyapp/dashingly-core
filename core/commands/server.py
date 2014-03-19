from flask.ext.script import Command, Manager, Option
from flask import current_app
import os
from app import app, initialize_app


class RunServer(Command):
    option_list = (
        Option('--port', '-p', dest='port'),
        Option('--hostname', '-hn', dest='host'),
    )

    def run(self, host="127.0.0.1", port=5000):
        if port is None:
            port = 5000
        port = int(port)
        app.run(debug=current_app.config['DEBUG'], host=host, port=port)
