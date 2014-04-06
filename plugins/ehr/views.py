from core.plugins.lib.fields import DataTypes
from core.plugins.lib.views.base import View
from core.plugins.lib.views.charts import ChartView, LineDescriptor, DailyCountChartView
from plugins.ehr.models import EHRData
from plugins.github.models import GithubCommits
import os
from flask import current_app

DATA_PATH = os.path.abspath(os.path.join(current_app.config['REPO_PATH'], "plugins", "ehr", "data"))

class EHRView(View):
    model = EHRData
    tags = ["ehr", "view"]

    def convert_lists(self, values, header):
        all_data = []
        for v in values:
            dat = {}
            for i in range(0, len(header)):
                dat[header[i]] = v[i]
            all_data.append(dat)
        return all_data


    def get(self, data):
       return self.get_ehr_data(data)

    def get_ehr_data(self, data):
        name = data.get('name', 'bob')
        file_path = os.path.abspath(os.path.join(DATA_PATH, "{0}.xml".format(name)))

        f = open(file_path, "r")
        xml = f.read()

        return {
            'ehr': xml
        }