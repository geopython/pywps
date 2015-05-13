"""Validator classes are used for ComplexInputs, to validate the content
"""

from pywps.validator import ValidatorAbstract
from pywps.validator import MODE
from pywps.formats import FORMATS
import mimetypes


class BasicValidator(ValidatorAbstract):
    """Data validator implements ValidatorAbstract class

    >>> from pywps.validator import MODE
    >>> open('file.json','w').write('{"foo": "bar"}')
    >>> class FakeInput:
    ...     source_type = 'file'
    ...     source = 'file.json'
    >>> fake_input = FakeInput()
    >>> validator = BasicValidator()
    >>> validator.validate(input, MODE.NONE)
    True
    """

    def validate(self, data_input, level=MODE.VERYSTRICT):
        """Perform input validation

        """
        return True

def validategml(data_input, mode):
    """GML validation example

    >>> import StringIO
    >>> class FakeInput(object):
    ...     gml = open('point.gml','w')
    ...     gml.write('''<?xml version="1.0" ?>
    ...     <gml:featureMember xmlns:gml="http://www.opengis.net/gml" xsi:schemaLocation="http://www.opengis.net/gml http://schemas.opengis.net/gml/2.1.2/feature.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><feature:feature xmlns:feature="http://example.com/feature"><feature:geometry><gml:Point><gml:coordinates decimal="." cs=", " ts=" ">-1, 1</gml:coordinates></gml:Point></feature:geometry></feature:feature></gml:featureMember>''')
    ...     gml.close()
    ...     file = 'point.gml'
    >>> class fake_data_format(object):
    ...     mimetype = 'application/gml+xml'
    >>> fake_input = FakeInput()
    >>> fake_input.data_format = fake_data_format()
    >>> validategml(fake_input, MODE.SIMPLE)
    True
    """
    passed = False

    if mode >= MODE.NONE:
        passed = True
    import sys

    if mode >= MODE.SIMPLE:

        _get_mimetypes()

        name = data_input.file
        (mtype, encoding) = mimetypes.guess_type(name, strict=False)
        passed = data_input.data_format.mime_type in {mtype, FORMATS['GML'][0]}

    if mode >= MODE.STRICT:

        from osgeo import ogr
        data_source = ogr.Open(data_input.file)
        if data_source:
            passed = (data_source.GetDriver().GetName() == "GML")
        else:
            passed = False

    if mode >= MODE.VERYSTRICT:

        from lxml import etree

        from pywps._compat import PY2
        if PY2:
            from urllib2 import urlopen
        else:
            from urllib.request import urlopen

        try:
            schema_url = data_input.data_format.schema
            gmlschema_doc = etree.parse(urlopen(schema_url))
            gmlschema = etree.XMLSchema(gmlschema_doc)
            passed = gmlschema.validate(etree.parse(data_input.stream))
        except:
            passed = False

    return passed

def validategeojson(data_input, mode):
    """GeoJSON validation example

    >>> import StringIO
    >>> class FakeInput(object):
    ...     json = open('point.geojson','w')
    ...     json.write('''{"type":"Feature", "properties":{}, "geometry":{"type":"Point", "coordinates":[8.5781228542328, 22.87500500679]}, "crs":{"type":"name", "properties":{"name":"urn:ogc:def:crs:OGC:1.3:CRS84"}}}''')
    ...     json.close()
    ...     file = 'point.geojson'
    >>> class fake_data_format(object):
    ...     mimetype = 'application/geojson'
    >>> fake_input = FakeInput()
    >>> fake_input.data_format = fake_data_format()
    >>> validategeojson(fake_input, MODE.SIMPLE)
    True
    """
    passed = False

    if mode >= MODE.NONE:
        passed = True

    if mode >= MODE.SIMPLE:

        _get_mimetypes()

        name = data_input.file
        (mtype, encoding) = mimetypes.guess_type(name, strict=False)
        passed = data_input.data_format.mime_type in {mtype, FORMATS['GEOJSON'][0]}

    if mode >= MODE.STRICT:

        from osgeo import ogr
        data_source = ogr.Open(data_input.file)
        if data_source:
            passed = (data_source.GetDriver().GetName() == "GeoJSON")
        else:
            passed = False

    if mode >= MODE.VERYSTRICT:

        import jsonschema
        import json

        # this code comes from
        # https://github.com/om-henners/GeoJSON_Validation/blob/master/geojsonvalidation/geojson_validation.py
        schema_home = os.path.join(_get_schemas_home(), "geojson")
        base_schema = os.path.join(schema_home, "geojson.json")
        geojson_base = json.load(open(base_schema))

        cached_json = {
            "http://json-schema.org/geojson/crs.json":
            json.load(open(os.path.join(schema_home, "crs.json"))),
            "http://json-schema.org/geojson/bbox.json":
            json.load(open(os.path.join(schema_home, "bbox.json"))),
            "http://json-schema.org/geojson/geometry.json":
            json.load(open(os.path.join(schema_home, "geometry.json")))
        }

        resolver = jsonschema.RefResolver(
            "http://json-schema.org/geojson/geojson.json",
            geojson_base, store=cached_json)

        validator = jsonschema.Draft4Validator(geojson_base, resolver=resolver)
        try:
            validator.validate(json.loads(data_input.stream.read()))
            passed = True
        except jsonschema.ValidationError:
            passed = False

    return passed

def validateshapefile(data_input, mode):
    """ESRI Shapefile validation example

    """
    passed = False

    if mode >= MODE.NONE:
        passed = True

    if mode >= MODE.SIMPLE:

        _get_mimetypes()
        name = data_input.file
        (mtype, encoding) = mimetypes.guess_type(name, strict=False)
        passed = data_input.data_format.mime_type in {mtype, FORMATS['SHP'][0]}

    if mode >= MODE.STRICT:

        from osgeo import ogr

        import zipfile
        z = zipfile.ZipFile(data_input.file)
        shape_name = None
        for name in z.namelist():
            z.extract(name, data_input.tempdir)
            if os.path.splitext(name)[1].lower() == '.shp':
                shape_name = name

        if shape_name:
            data_source = ogr.Open(os.path.join(data_input.tempdir, shape_name))

        if data_source:
            passed = (data_source.GetDriver().GetName() == "ESRI Shapefile")
        else:
            passed = False

    return passed

def _get_schemas_home():
    """Get path to schemas directory
    """
    return os.path.join(
        os.path.abspath(
            os.path.dirname(__file__)
        ),
        os.path.pardir,
        "schemas")

def _get_mimetypes():
    from pywps.formats import FORMATS
    mimetypes.init()
    for pywps_format in FORMATS:
        (mtype, ext) = FORMATS[pywps_format]

        # NOTE: strict is set to True: mimetype will be added to system
        # mimetypes, zip -> application/zipped-shapefile
        mimetypes.add_type(mtype, ext, True)


if __name__ == "__main__":
    import doctest

    import os
    from pywps.wpsserver import temp_dir

    with temp_dir() as tmp:
        os.chdir(tmp)
        doctest.testmod()
