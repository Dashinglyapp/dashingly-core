class MetricManager(object):
    def __init__(self, user):
        self.user = user

    def list(self):
        return self.user.metrics

    def lookup_metric(self, metric_name):
        from core.database.models import Metric, db
        return db.session.query(Metric).filter(Metric.name == metric_name).first()