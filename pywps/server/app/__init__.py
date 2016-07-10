import flask

from flask_sqlalchemy import SQLAlchemy

from pywps.server.app.pywps_flask import PyWPSFlask


application = PyWPSFlask(__name__)

# expire_on_commit was added due to this situation: http://stackoverflow.com/questions/15750557/sqlalchemy-why-create-a-sessionmaker-before-assign-it-to-a-session-object
db = SQLAlchemy(application, session_options={'expire_on_commit': False})


from pywps.server.app import views, models