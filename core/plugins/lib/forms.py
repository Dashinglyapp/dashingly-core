from flask_wtf import Form
from wtforms import FloatField, IntegerField, TextField
from datetime import datetime
from core.plugins.lib.views import WidgetView

class JSONMixin(object):
    def as_json(self):
        form = {}
        form['csrf_token'] = self.generate_csrf_token()
        fields = []
        for f in self:
            field = dict(
                name=f.name,
                short_name=f.short_name,
                id=f.id,
                label=f.label,
                default=f.default,
                description=f.description,
                errors=f.errors,
                type=f.type,
                flags=f.flags.__dict__,
                data=f.data,
                raw_data=f.raw_data,
                widget=f.widget.__dict__,
                object_data=f.object_data
            )
            fields.append(field)
        form['fields'] = fields
        return form


class FormWidget(Form, WidgetView, JSONMixin):
    metric_proxy = None
    plugin_proxy = None
    source_proxy = None
    model = None
    tags = ["form", "widget"]

    def to_json(self, data):
        return self.as_json()

    def post(self, data):
        return self.save(data)

    def save(self, data):
        if self.validate():
            mod = self.model(**data)
            mod.date = datetime.utcnow()
            self.manager.add(mod)
            return {'status': 200}
        else:
            return self._errors

class SettingsFormWidget(FormWidget):
    def save(self, data):
        data = self.data
        mod = self.model(**data)
        mod = self.manager.get_or_create(mod, query_data=False)
        for attr in data:
            setattr(mod, attr, data[attr])
        self.manager.update(mod)