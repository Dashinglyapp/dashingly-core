from core.plugins.tasks import TaskBase, Interval
from core.plugins.proxies import TaskProxy

class ScrapeTask(TaskBase):
    interval = Interval.hourly
    task_proxy = TaskProxy(name="scrape")

    def run(self):
        pass

