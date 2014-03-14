from flask.ext.script import Command

class BaseCommand(Command):
    option_list = []
    name = None

    def run(self, **kwargs):
        self.run_command(**kwargs)

    def run_command(self, **kwargs):
        raise NotImplementedError()