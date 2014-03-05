from fields import DataTypes

class BaseView(object):
    name = None
    manager = None
    path = None
    children = []
    tags = ["view"]

    def __init__(self, **kwargs):
        for k in kwargs:
            setattr(self, k, kwargs[k])

    def get(self, data):
        raise NotImplementedError()

    def post(self, data):
        raise NotImplementedError()

    def delete(self, data):
        raise NotImplementedError

    def put(self, data):
        raise NotImplementedError()

    def patch(self, data):
        raise NotImplementedError()

class WidgetView(BaseView):
    name = None
    description = None
    hashkey = None
    path = None
    children = []
    tags = ["widget"]

    def get(self, data):
        data = self.to_json(data)
        meta = self.__class__.meta()
        meta.update({
            'data': data
        })
        return meta

    @classmethod
    def meta(cls):
        return {
            'tree': cls.tree(),
            'name': cls.name,
            'description': cls.description,
            'hashkey': cls.hashkey,
            'url': cls.path,
            'tags': cls.tags
        }

    def post(self, data):
        raise NotImplementedError()

    def save(self, **kwargs):
        raise NotImplementedError()

    @classmethod
    def tree(cls):
        widgets = []
        for w in cls.children:
            widgets.append(w.meta())
        return widgets

    def to_json(self, data):
        return {}

class LineDescriptor(object):
    def __init__(self, type, label, description, name, data):
        self.type = type
        self.label = label
        self.description = description
        self.data = data
        self.name = name

class ChartWidget(WidgetView):
    name = None
    description = None
    tags = ["widget", "chart"]

    def get_chart_points(self, data):
        raise NotImplementedError()

    def to_json(self, data):
        chart_points = self.get_chart_points(data)
        return {
            'x': chart_points['x'].__dict__,
            'y': [y.__dict__ for y in chart_points['y']],
        }

class ModelChartWidget(ChartWidget):
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