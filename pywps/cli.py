##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

import os
import sys
import click
import signal
import threading
from werkzeug.serving import run_simple
from pywps.app.Service import Service
from pywps import configuration
from pywps.queue import JobQueueService

import sqlalchemy
from alembic.config import Config
from alembic import command

from urllib.parse import urlparse

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


def get_host(cfgfiles=None):
    configuration.load_configuration(cfgfiles)
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
@click.option('--config', '-c', metavar='PATH', help='path to pywps configuration file.')
@click.pass_context
def cli(ctx, config):
    """Command line to start/stop a PyWPS service.

    Do not use this service in a production environment.
    It's intended to be running in a test environment only!
    For more documentation, visit http://pywps.org/doc
    """
    ctx.ensure_object(dict)
    ctx.obj['CFG_FILES'] = []
    if config:
        ctx.obj['CFG_FILES'].append(config)


@cli.command()
@click.option('--bind-host', '-b', metavar='IP-ADDRESS', default='127.0.0.1',
              help='IP address used to bind service.')
@click.option('--no-jobqueue', '-n', is_flag=True,
              help='Do not start job queue service.')
@click.pass_context
def start(ctx, bind_host, no_jobqueue):
    """Start PyWPS service.
    This service is by default available at http://localhost:5000/wps
    """
    app = Service(cfgfiles=ctx.obj['CFG_FILES'])

    def inner(application, bind_host=None):
        # call this *after* app is initialized ... needs pywps config.
        host, port = get_host(cfgfiles=ctx.obj['CFG_FILES'])
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
        jq_service = JobQueueService(cfgfiles=ctx.obj['CFG_FILES'])
        signal.signal(signal.SIGTERM, lambda *args: sys.exit(0))
        try:
            t = threading.Thread(target=inner, args=(app, bind_host))
            t.setDaemon(True)
            t.start()
            jq_service.run()
        except KeyboardInterrupt:
            pass


@cli.command()
@click.pass_context
def jobqueue(ctx):
    """Start job queue service.
    """
    jq_service = JobQueueService(cfgfiles=ctx.obj['CFG_FILES'])
    signal.signal(signal.SIGTERM, lambda *args: sys.exit(0))
    click.echo('Starting job queue service (Press CTRL+C to quit)')
    try:
        jq_service.run()
    except KeyboardInterrupt:
        pass


@cli.command()
@click.option('--force', '-f', is_flag=True,
              help='Force dropping exising database.')
@click.pass_context
def migrate(ctx, force):
    """Upgrade or initialize database.
    """
    if ctx.obj['CFG_FILES']:
        os.environ['PYWPS_CFG'] = ctx.obj['CFG_FILES'][0]
    if force:
        click.echo('dropping database')
        _drop_db()
    click.echo('migrating database')
    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", "pywps:alembic")
    command.upgrade(alembic_cfg, "head")


def _drop_db():
    database = configuration.get_config_value('logging', 'database')
    engine = sqlalchemy.create_engine(database, echo=False)
    for table in engine.table_names():
        sql = sqlalchemy.text("DROP TABLE IF EXISTS {}".format(table))
        engine.execute(sql)
