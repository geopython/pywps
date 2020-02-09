from pywps.app.Service import Service


def make_app(processes=None, cfgfiles=None):
    app = Service(processes=processes, cfgfiles=cfgfiles)
    return app
