from flask import Flask
from core.web.main_views import main_views
from core.web.plugin_views import plugin_views
from flask.ext.security import Security, SQLAlchemyUserDatastore
import settings

app = Flask(__name__, template_folder='templates')
app.register_blueprint(main_views)
app.register_blueprint(plugin_views)

app.config.from_object('settings')

if __name__ == '__main__':
    from core.database.models import db, User, Role
    db.create_all()
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security = Security(app, user_datastore)
    app.run(debug=settings.DEBUG)