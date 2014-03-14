from celery import states
from celery.utils.encoding import safe_repr
from celery.utils import get_full_cls_name, kwdict
from flask import Blueprint, jsonify
from core.util import append_container, DEFAULT_SECURITY
from flask import current_app
from realize.log import logging
import os
from flask.ext.restful import Resource, Api
from flask.ext.restful import reqparse
from flask_restful_swagger import swagger

log = logging.getLogger(__name__)

task_views = Blueprint('task_views', __name__, template_folder=os.path.join(current_app.config['REPO_PATH'], 'templates'))
api = swagger.docs(Api(task_views), api_spec_url=current_app.config['API_SPEC_URL'])

class TaskStatus(Resource):
    method_decorators = [DEFAULT_SECURITY]

    def get(self, task_id):
        from app import celery

        result = celery.AsyncResult(task_id)
        state, retval = result.state, result.result
        response_data = dict(id=task_id, status=state)
        if state in states.EXCEPTION_STATES:
            traceback = result.traceback
            response_data.update({'exc': get_full_cls_name(retval.__class__),
                                  'traceback': traceback})
        return {'task': response_data}

api.add_resource(TaskStatus, '/api/v1/tasks/<string:task_id>')