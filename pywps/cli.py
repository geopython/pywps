###########################################################
# Demo WPS service for testing and debugging.
#
# See the werkzeug documentation on how to use the debugger:
# http://werkzeug.pocoo.org/docs/0.12/debug/
###########################################################

import os
import sys
import click
import signal
import threading
from werkzeug.serving import run_simple
from pywps.app.Service import Service
from pywps import configuration
from pywps.queue import JobQueueService

from alembic.config import Config
from alembic import command

from urllib.parse import urlparse

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


def get_host():
    url = configuration.get_config_value('server', 'url')
    url = url or 'http://localhost:5000/wps'

    click.echo("starting WPS service on {}".format(url))

    parsed_url = urlparse(url)
    if ':' in parsed_url.netloc:
        host, port = parsed_url.netloc.split(':')
        port = int(port)
    else:
        host = parsed_url.netloc
        port = 80
    return host, port


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option()
def cli():
    """Command line to start/stop a PyWPS service.

    Do not use this service in a production environment.
    It's intended to be running in a test environment only!
    For more documentation, visit http://pywps.org/doc
    """
    pass


@cli.command()
@click.option('--config', '-c', metavar='PATH', help='path to pywps configuration file.')
@click.option('--bind-host', '-b', metavar='IP-ADDRESS', default='127.0.0.1',
              help='IP address used to bind service.')
@click.option('--no-jobqueue', '-n', is_flag=True,
              help='Do not start job queue service.')
def start(config, bind_host, no_jobqueue):
    """Start PyWPS service.
    This service is by default available at http://localhost:5000/wps
    """
    if config:
        os.environ['PYWPS_CFG'] = config
    app = Service()

    def inner(application, bind_host=None):
        # call this *after* app is initialized ... needs pywps config.
        host, port = get_host()
        bind_host = bind_host or host
        # need to serve the wps outputs
        static_files = {
            '/outputs': configuration.get_config_value('server', 'outputpath')
        }
        run_simple(
            hostname=bind_host,
            port=port,
            application=application,
            use_debugger=False,
            use_reloader=False,
            threaded=True,
            # processes=2,
            use_evalex=True,
            static_files=static_files)
    # let's start the service ...
    # See:
    # * https://github.com/geopython/pywps-flask/blob/master/demo.py
    # * http://werkzeug.pocoo.org/docs/0.14/serving/
    if no_jobqueue:
        click.echo('Starting pywps without job queue')
        inner(app, bind_host)
    else:
        click.echo('Starting pywps with job queue')
        jq_service = JobQueueService()
        signal.signal(signal.SIGTERM, lambda *args: sys.exit(0))
        try:
            t = threading.Thread(target=inner, args=(app, bind_host))
            t.setDaemon(True)
            t.start()
            jq_service.run()
        except KeyboardInterrupt:
            pass


@cli.command()
@click.option('--config', '-c', metavar='PATH', help='path to pywps configuration file.')
def jobqueue(config):
    """Start job queue service.
    """
    if config:
        os.environ['PYWPS_CFG'] = config
    jq_service = JobQueueService()
    signal.signal(signal.SIGTERM, lambda *args: sys.exit(0))
    click.echo('Starting job queue service (Press CTRL+C to quit)')
    try:
        jq_service.run()
    except KeyboardInterrupt:
        pass


@cli.command()
@click.option('--config', '-c', metavar='PATH', help='path to pywps configuration file.')
def migrate(config):
    """Uprade or initialize database.
    """
    if config:
        os.environ['PYWPS_CFG'] = config
    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", "pywps:alembic")
    command.upgrade(alembic_cfg, "head")
