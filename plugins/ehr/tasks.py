import csv
import random
from core.plugins.lib.models import DuplicateRecord
from core.plugins.lib.tasks import TaskBase, Interval
from core.plugins.lib.proxies import TaskProxy
from datetime import datetime, timedelta
from plugins.ehr.models import EHRData
from plugins.github.models import GithubCommits
from core.plugins.lib.proxies import MetricProxy
from plugins.github import manifest
import pytz
from dateutil import parser
from flask import current_app
import os

DATA_PATH = os.path.abspath(os.path.join(current_app.config['REPO_PATH'], "plugins", "ehr", "data"))

class ImportTask(TaskBase):
    task_proxy = TaskProxy(name="import")

    def run(self):

        patient_files = [f for f in os.listdir(DATA_PATH)]
        header_var = "PatientGuid"
        random_guid = None
        all_data = {}

        for (i, f) in enumerate(patient_files):
            file_path = os.path.abspath(os.path.join(DATA_PATH, f))
            with open(file_path, 'rb') as csvfile:
                reader = csv.reader(csvfile)
                data = []
                all_data[f] = {'header': None, 'data': []}
                for (i, r) in enumerate(reader):
                    if i == 0:
                        header = r
                    if header_var in header:
                        all_data[f]['header'] = header
                        header_num = None
                        for (i, h) in enumerate(header):
                            if h == header_var:
                                header_num = i
                        for r in reader:
                            data.append(r)
                        if random_guid is None:
                            random_int = random.randint(0, len(data))
                            random_guid = data[random_int][header_num]
                        for d in data:
                            if d[header_num] == random_guid:
                                all_data[f]['data'].append(d)
        obj = EHRData(data=all_data)
        try:
            self.manager.add(obj)
        except DuplicateRecord:
            pass
