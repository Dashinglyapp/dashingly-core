from flask.ext.script import Command, Manager, Option
from subprocess import Popen

class Test(Command):
    def run_command(self, command):
        cmd = Popen(command, shell=True)
        cmd.wait()

    def run(self):
        self.run_command("nosetests --with-coverage --cover-package='core' --logging-level='INFO'")