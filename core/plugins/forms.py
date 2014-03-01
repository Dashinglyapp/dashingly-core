from flask_wtf import Form
from wtforms import FloatField, IntegerField, TextField
from datetime import datetime


class BaseForm(Form):
    metric_proxy = None
    plugin_proxy = None
    source_proxy = None
    model = None

    def save(self):
        mod = self.model(**self.data)
        mod.date = datetime.utcnow()
        self.manager.add(mod)

    def as_json(self):
        fields = {}
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
                widget=f.widget.__dict__
            )
            fields[f.name] = field
        return fields

class SettingsForm(BaseForm):
    def save(self):
        data = self.data
        mod = self.model(**data)
        mod = self.manager.get_or_create(mod, query_data=False)
        for attr in data:
            setattr(mod, attr, data[attr])
        self.manager.update(mod)