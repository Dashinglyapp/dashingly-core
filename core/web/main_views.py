from flask import Blueprint, render_template, abort, request, url_for
from werkzeug.utils import redirect
from core.metrics.manager import MetricManager
import settings
import os
from flask.ext.security import login_required
from flask.ext.login import current_user

from flask.views import MethodView

main_views = Blueprint('main_views', __name__, template_folder=os.path.join(settings.REPO_PATH, 'templates'))

@main_views.route('/')
def index():
    return render_template("index.html")

@main_views.route('/plugins/list')
@login_required
def manage_plugins():
    from core.plugins.loader import plugins
    from core.plugins.manager import PluginManager
    installed_plugins = PluginManager(current_user).list()
    return render_template("plugins.html", available_plugins=plugins, installed_plugins=[p.hashkey for p in installed_plugins])

@main_views.route('/metrics')
@login_required
def metrics():
    manager = MetricManager(current_user)
    return render_template("metrics.html", installed_metrics=manager.list())

class Forms(MethodView):
    decorators = [login_required]

    def get(self):
        from core.plugins.loader import plugins
        plugin_keys = [p.hashkey for p in current_user.plugins]
        forms = []
        for p in plugin_keys:
            forms += plugins[p].forms
        form_html = []
        for f in forms:
            form = render_template('forms/basic_form.html', form=f(request.form))
            form_html.append({'form': form, 'metric': f.metric_proxy, 'plugin': f.plugin_proxy})

        return render_template('forms.html', form_html=form_html)

    def post(self):
        from core.plugins.manager import PluginManager
        vals = request.form
        plugin_key = vals['plugin']
        metric_name = vals['metric']

        new_vals = {}
        for v in vals:
            if v not in ['plugin', 'metric', 'source']:
                new_vals[v] = vals[v]

        manager = PluginManager(current_user)
        data = manager.save_form(plugin_key, metric_name, **new_vals)

        return redirect(url_for('main_views.forms'))

main_views.add_url_rule('/forms', view_func=Forms.as_view('forms'))