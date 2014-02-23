from flask_wtf import Form
from wtforms import FloatField, IntegerField, TextField

class BaseForm(Form):
    metric_proxy = None
    plugin_proxy = None
    source_proxy = None

    def save(self):
        raise NotImplementedError()
