from celery import states
from celery.utils.encoding import safe_repr
from celery.utils import get_full_cls_name, kwdict
from flask import Blueprint, jsonify
from core.util import append_container
from realize import settings
from realize.log import logging
import os

log = logging.getLogger(__name__)

task_views = Blueprint('task_views', __name__, template_folder=os.path.join(settings.REPO_PATH, 'templates'))

@task_views.route('/api/v1/tasks/<string:task_id>')
def task_status(task_id):
    """
    Returns task status and result in JSON format.
    """
    from app import celery

    result = celery.AsyncResult(task_id)
    state, retval = result.state, result.result
    response_data = dict(id=task_id, status=state)
    if state in states.EXCEPTION_STATES:
        traceback = result.traceback
        response_data.update({'exc': get_full_cls_name(retval.__class__),
                              'traceback': traceback})
    return jsonify(append_container({'task': response_data}))