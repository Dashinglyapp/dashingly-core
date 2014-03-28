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

        frontend_path = os.path.abspath(os.path.join(current_app.config['REPO_PATH'], current_app.config['FRONTEND_PATH']))
        for the_file in os.listdir(current_app.config['FRONTEND_PATH']):
            file_path = os.path.join(current_app.config['FRONTEND_PATH'], the_file)
            try:
                if os.path.isfile(file_path) and the_file != ".vc":
                    os.unlink(file_path)
            except Exception, e:
                print e
        self.run_command("npm install")
        self.run_command("grunt setup")
        self.run_command("rm -rf {0}/*".format(frontend_path))
        self.run_command("cp -a dist/* {0}".format(os.path.abspath(frontend_path)))