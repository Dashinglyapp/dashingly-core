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
            'additional_info': chart_points.get('additional_info', None),
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

class DailyCountChartView(ChartView):
    model = None
    x_label = None
    y_label = None
    x_description = None
    y_description = None
    x_name = None
    y_name = None
    x_data_field = None
    y_data_field = None

    # One of 'average', 'count', 'first', 'last', and 'total'
    aggregation_method = "average"
    tags = ["view", "chart", "daily-count-timeseries"]

    def get_chart_points(self, data):
        start = data.get('start', None)
        end = data.get('end', None)

        data = self.manager.query_class_range("date", self.model, start=start, end=end)

        counts = {}
        values = {}
        totals = {}

        last_times = {}
        for d in data:
            tz_date = self.convert_to_local_timezone(getattr(d, self.x_data_field))
            date_obj = tz_date.replace(hour=0, minute=0, second=0, microsecond=0)
            date_str = date_obj.isoformat()
            if date_str in counts:
                counts[date_str] += 1
            else:
                counts[date_str] = 1
            if self.aggregation_method in ["last", "first"]:
                last_time = last_times.get(date_str, None)
                value = getattr(d, self.y_data_field)
                updated = False
                if self.aggregation_method == "last" and last_time is None or last_time < tz_date:
                    values[date_str] = value
                    updated = True
                elif self.aggregation_method == "first" and last_time is None or last_time > tz_date:
                    values[date_str] = value
                    updated = True
                if updated:
                    last_times[date_str] = tz_date
            elif self.aggregation_method in ['total', 'average']:
                value = getattr(d, self.y_data_field)
                if date_str in totals:
                    totals[date_str] += value
                else:
                    totals[date_str] = value

        info = counts
        if self.aggregation_method == "average":
            info = {}
            for d in totals:
                info[d] = totals[d] / float(counts[d])
        elif self.aggregation_method == "total":
            info = totals
        elif self.aggregation_method in ["last", "first"]:
            info = values

        x = info.keys()
        x.sort()
        y = [info[i] for i in x]

        x = LineDescriptor(type=DataTypes.integer, label=self.x_label, description=self.x_name, name=self.x_name, data=x)
        y = LineDescriptor(type=DataTypes.date, label=self.y_label, description=self.y_name, name=self.y_name, data=y)

        return {
            'x': x,
            'y': [y]
        }