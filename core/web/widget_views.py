from flask import Blueprint, render_template, abort, request, jsonify
from flask.ext.security import login_required
from flask.ext.login import current_user
from flask import redirect, url_for
from flask.views import MethodView
from core.database.models import WidgetModel
from core.manager import ExecutionContext
from core.util import DEFAULT_SECURITY, append_container
from realize import settings
import os
from flask import current_app
from realize.log import logging
import json
log = logging.getLogger(__name__)

widget_views = Blueprint('widget_views', __name__, template_folder=os.path.join(settings.REPO_PATH, 'templates'))

@widget_views.route('/api/v1/widgets')
@DEFAULT_SECURITY
def widget_list():
    from app import db
    widget_models = db.session.query(WidgetModel.name).filter(WidgetModel.user == current_user).all()
    if len(widget_models) == 1:
        widget_models = [widget_models]
    widgets = []
    for w in widget_models:
        name = w[0]
        url = url_for('widget_views.widget_settings', widget_name=name)
        widgets.append(dict(name=name, url=url))
    return jsonify(append_container(widgets, code=200, name="widget_list"))

class WidgetSettings(MethodView):
    decorators = [DEFAULT_SECURITY]

    def get_model(self, widget_name):
        from app import db
        model = db.session.query(WidgetModel).filter(WidgetModel.user == current_user, WidgetModel.name == widget_name).first()
        if model is None:
            model = WidgetModel(
                user=current_user,
                name=widget_name,
                version=settings.WIDGET_SETTINGS_VERSION,
                settings=json.dumps({})
            )
            db.session.add(model)
            db.session.commit()
        try:
            model_settings = json.loads(model.settings)
        except ValueError:
            model_settings = {}
        return model, model_settings

    def get(self, widget_name):
        model, model_settings = self.get_model(widget_name)
        return jsonify(append_container(model_settings, name="widget_settings", data_key='settings'))

    def post(self, widget_name):
        from app import db
        model, model_settings = self.get_model(widget_name)
        new_settings = request.json.get('settings', model_settings)
        model.settings = json.dumps(new_settings)
        db.session.commit()
        return jsonify(append_container("", code=201))

    def delete(self, widget_name):
        from app import db
        model, model_settings = self.get_model(widget_name)
        model.settings = json.dumps({})
        db.session.commit()
        return jsonify(append_container("", code=204))

widget_views.add_url_rule('/api/v1/widgets/<string:widget_name>/settings', view_func=WidgetSettings.as_view('widget_settings'))
