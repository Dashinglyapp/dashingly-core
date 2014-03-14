from flask.ext.script import Command, Manager, Option
from flask import current_app
import os
from subprocess import Popen


class InvalidPathException(Exception):
    pass

class SyncJS(Command):
    option_list = (
        Option('--path', '-p', dest='path'),
    )

    def run_command(self, command):
        cmd = Popen(command, shell=True, cwd=self.cwd)
        cmd.wait()

    def run(self, path=None):
        if path is None:
            raise InvalidPathException
        path = os.path.expanduser(path)
        self.cwd = os.path.abspath(path)
        self.run_command("npm install")
        self.run_command("bower install")
        self.run_command("grunt fullBuild")
        self.run_command("cp -a build/app/* {0}".format(os.path.abspath(os.path.join(current_app.config['REPO_PATH'], current_app.config['FRONTEND_PATH']))))