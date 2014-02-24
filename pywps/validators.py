from abc import ABCMeta, abstractmethod, abstractproperty
from formats import FORMATS
import os

class MODE(object):
    NONE = 0
    SIMPLE = 1
    STRICT = 2
    VERYSTRICT = 3

class ValidatorAbstract(object):
    """Data validator abstract class
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def validate(self, input, level=MODE.VERYSTRICT):
        """Perform input validation
        """
        pass

class BasicValidator(ValidatorAbstract):
    """Data validator implements ValidatorAbstract class

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
        if level > MODE.NONE:
            data_input.data_format.validator.validate(data_input)
        else:
            return True
        pass

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

        import mimetypes
        from formats import FORMATS
        mimetypes.init()
        for pywps_format in FORMATS:
            (mtype, ext) = FORMATS[pywps_format]
            mimetypes.add_type(mtype, ext, False)

        name = data_input.file
        (mtype, encoding) = mimetypes.guess_type(name, strict=False)
        passed = (mtype == data_input.data_format.mimetype == FORMATS['GML'][0])

    if mode >= MODE.STRICT:

        from osgeo import ogr
        data_source = ogr.Open(data_input.file)
        if data_source:
            passed = (data_source.GetDriver().GetName() == "GML")
        else:
            passed = False

    if mode >= MODE.VERYSTRICT:

        from lxml import etree
        from urllib2 import urlopen
        schema_url = data_input.data_format.schema
        gmlschema_doc = etree.parse(urlopen(schema_url))
        gmlschema = etree.XMLSchema(gmlschema_doc)
        return gmlschema.validate(etree.parse(data_input.stream))

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

        import mimetypes
        from formats import FORMATS
        mimetypes.init()
        for pywps_format in FORMATS:
            (mtype, ext) = FORMATS[pywps_format]
            mimetypes.add_type(mtype, ext, False)

        name = data_input.file
        (mtype, encoding) = mimetypes.guess_type(name, strict=False)
        passed = (mtype == data_input.data_format.mimetype == FORMATS['GEOJSON'][0])

    if mode >= MODE.STRICT:

        from osgeo import ogr
        data_source = ogr.Open(data_input.file)
        if data_source:
            passed = (data_source.GetDriver().GetName() == "GeoJSON")
        else:
            passed = False

    if mode >= MODE.VERYSTRICT:

        import jsonschema, json

        # this code comes from
        # https://github.com/om-henners/GeoJSON_Validation/blob/master/geojsonvalidation/geojson_validation.py

        # TODO: more robust way, how to define schemas
        _schema_home = os.path.join(
            os.path.abspath(
                os.path.dirname(__file__)
            ), os.path.pardir,
            "schemas",
            "geojson"
        )

        geojson_base = json.load(
            open(
                os.path.join(
                    _schema_home,
                    "geojson.json"
                )
            )
        )

        cached_json = {
            "http://json-schema.org/geojson/crs.json": json.load(open(os.path.join(_schema_home, "crs.json"))),
            "http://json-schema.org/geojson/bbox.json": json.load(open(os.path.join(_schema_home, "bbox.json"))),
            "http://json-schema.org/geojson/geometry.json": json.load(open(os.path.join(_schema_home, "geometry.json"))),
        }

        resolver = jsonschema.RefResolver(
            "http://json-schema.org/geojson/geojson.json",
            geojson_base,
            store=cached_json
        )

        validator = jsonschema.Draft4Validator(geojson_base, resolver=resolver)
        try:
            validator.validate(json.loads(data_input.stream.read()))
            passed = True
        except jsonschema.ValidationError:
            passed = False

    return passed


if __name__ == "__main__":
    import doctest

    import tempfile, os
    from contextlib import contextmanager
    from path import path
    @contextmanager
    def temp_dir():
        tmp = path(tempfile.mkdtemp())
        try:
            yield tmp
        finally:
            tmp.rmtree()

    with temp_dir() as tmp:
        os.chdir(tmp)
        doctest.testmod()
