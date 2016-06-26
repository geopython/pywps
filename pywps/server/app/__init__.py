import flask
import flask_sqlalchemy

from pywps.server.app.main import MyFlask


application = MyFlask(__name__)
application.config['SQLALCHEMY_DATABASE_URI'] = r'postgresql://pywps_db_user@localhost/pywps'
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = flask_sqlalchemy.SQLAlchemy(application)


from pywps.server.app import views, models

