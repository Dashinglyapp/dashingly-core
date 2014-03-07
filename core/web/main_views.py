from flask import Blueprint, render_template
from flask.ext.security.utils import md5
from realize import settings
import os
from realize.log import logging

log = logging.getLogger(__name__)

main_views = Blueprint('main_views', __name__, template_folder=os.path.join(settings.REPO_PATH, 'templates'))

@main_views.route('/')
def index():
    return render_template("index.html")
