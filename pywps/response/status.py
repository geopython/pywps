from collections import namedtuple
from werkzeug.wrappers import Response
import json
from pywps.inout.array_encode import ArrayEncoder
from pywps.app.basic import get_json_indent
from jinja2 import Environment, PackageLoader
import os
from pywps.translations import get_translation

from . import RelEnvironment

_WPS_STATUS = namedtuple('WPSStatus', ['UNKNOWN', 'ACCEPTED', 'STARTED', 'PAUSED', 'SUCCEEDED', 'FAILED'])
WPS_STATUS = _WPS_STATUS(0, 1, 2, 3, 4, 5)


class StatusResponse(Response):
    def __init__(self, json_data, mimetype):

        template_env = RelEnvironment(
            loader=PackageLoader('pywps', 'templates'),
            trim_blocks=True, lstrip_blocks=True,
            autoescape=True,
        )
        template_env.globals.update(get_translation=get_translation)

        if mimetype == 'application/json':
            doc = json.dumps(self._render_json_response(json_data), cls=ArrayEncoder, indent=get_json_indent())
        else:
            template = template_env.get_template(json_data["version"] + '/execute/main.xml')
            doc = template.render(**json_data)
        super(StatusResponse, self).__init__(response=doc, mimetype=mimetype)

    @staticmethod
    def _render_json_response(jdoc):
        response = dict()
        response['status'] = jdoc['status']
        out = jdoc['process']['outputs']
        d = {}
        for val in out:
            id = val.get('identifier')
            if id is None:
                continue
            type = val.get('type')
            key = 'bbox' if type == 'bbox' else 'data'
            if key in val:
                d[id] = val[key]
        response['outputs'] = d
        return response
