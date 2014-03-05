from core.plugins.lib.views.base import View
from core.plugins.lib.fields import DataTypes

class LineDescriptor(object):
    def __init__(self, type, label, description, name, data):
        self.type = type
        self.label = label
        self.description = description
        self.data = data
        self.name = name

class ChartView(View):
    name = None
    description = None
    tags = ["view", "chart"]

    def get_chart_points(self, data):
        raise NotImplementedError()

    def to_json(self, data):
        chart_points = self.get_chart_points(data)
        return {
            'x': chart_points['x'].__dict__,
            'y': [y.__dict__ for y in chart_points['y']],
            }

class ModelChartView(ChartView):
    model = None
    y_data_field = None
    x_data_field = None
    x_label = None
    y_label = None
    x_description = None
    y_description = None
    x_name = None
    y_name = None

    def get_chart_points(self, data):
        start = data.get('start', None)
        end = data.get('end', None)
        data = self.manager.query_class_range("date", self.model, start=start, end=end)
        x_points = [getattr(d, self.x_data_field) for d in data]
        y_points = [getattr(d, self.y_data_field) for d in data]

        if len(data) == 0:
            x_type = DataTypes.none
            y_type = DataTypes.none
        else:
            x_type = getattr(self.model, self.x_data_field).datatype
            y_type = getattr(self.model, self.y_data_field).datatype

        x = LineDescriptor(type=x_type, label=self.x_label, description=self.x_description, name=self.x_name, data=x_points)
        y = LineDescriptor(type=y_type, label=self.y_label, description=self.y_description, name=self.y_name, data=y_points)

        return {
            'x': x,
            'y': [y]
        }