from core.plugins.forms import BaseForm, TextField, IntegerField, FloatField
import manifest
from core.plugins.proxies import MetricProxy, SourceProxy

class SurveyForm(BaseForm):
    heading = "Please enter some information about your mood."
    display_fields = ['text', 'number']
    metric_proxy = MetricProxy(name="data")
    source_proxy = SourceProxy(name="self")
    plugin_proxy = manifest.plugin_proxy

    text = TextField(description="Enter the mood you are feeling.")
    number = IntegerField(description="Number on a 1-10 scale.")
