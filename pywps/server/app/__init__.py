from flask_sqlalchemy import SQLAlchemy

from pywps.server.app.pywps_flask import PyWPSFlask

#from multiprocessing.util import register_after_fork



application = PyWPSFlask(__name__)
# To disable SQLALCHEMY_TRACK_MODIFICATIONS warning [1]
# [1] http://stackoverflow.com/questions/33738467/how-do-i-know-if-i-can-disable-sqlalchemy-track-modifications
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# expire_on_commit session option added because of [1]
# [1] http://stackoverflow.com/questions/15750557/sqlalchemy-why-create-a-sessionmaker-before-assign-it-to-a-session-object
db = SQLAlchemy(application, session_options={'expire_on_commit': False})

#register_after_fork(db.get_engine(application), db.get_engine(application).dispose)

from pywps.server.app import views, models