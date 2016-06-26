import flask

from flask_sqlalchemy import SQLAlchemy

from pywps.server.app.pywps_flask import PyWPSFlask


application = PyWPSFlask(__name__)

db = SQLAlchemy(application)


from pywps.server.app import views, models