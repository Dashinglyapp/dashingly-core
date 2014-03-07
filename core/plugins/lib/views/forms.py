from flask_wtf import Form
from wtforms import FloatField, IntegerField, TextField
from datetime import datetime
from core.plugins.lib.views.base import View

class JSONMixin(object):
    def as_json(self):
        form = {}
        form['csrf_token'] = self.generate_csrf_token()
        fields = []
        for f in self._fields:
            f_obj = self._fields[f]
            field = f_obj.__dict__.copy()
            field['errors'] = f_obj.errors
            field['widget'] = f_obj.widget.input_type
            del field['_translations']
            del field['validators']
            del field['object_data']
            field['flags'] = field['flags'].__dict__
            field['label'] = field['label'].__dict__
            field['value'] = getattr(self, f, None)
            fields.append(field)
        form['fields'] = fields
        return form


class FormView(Form, View, JSONMixin):
    metric_proxy = None
    plugin_proxy = None
    source_proxy = None
    model = None
    tags = ["form", "view"]

    def to_json(self, data):
        return self.as_json()

    def post(self, data):
        if self.validate():
            self.save(data)
            return {'status': 200}

        return self.errors

    def save(self, data):
        mod = self.model(**data)
        mod.date = datetime.utcnow()
        self.manager.add(mod)


class SettingsFormView(FormView):
    def save(self, data):
        data = self.data
        mod = self.model(**data)
        mod = self.manager.get_or_create(mod, query_data=False)
        for attr in data:
            setattr(mod, attr, data[attr])
        self.manager.update(mod)