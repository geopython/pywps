##################################################################
# Copyright 2018 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

"""Validator classes are used for ComplexInputs, to validate the content
"""


import logging

from pywps.validator.mode import MODE
from pywps.inout.formats import FORMATS
import mimetypes
import os

from pywps._compat import PY2
if PY2:
    from urllib2 import urlopen
else:
    from urllib.request import urlopen

LOGGER = logging.getLogger('PYWPS')


def validategml(data_input, mode):
    """GML validation function

    :param data_input: :class:`ComplexInput`
    :param pywps.validator.mode.MODE mode:

    This function validates GML input based on given validation mode. Following
    happens, if `mode` parameter is given:

    `MODE.NONE`
        it will return always `True`
    `MODE.SIMPLE`
        the mimetype will be checked
    `MODE.STRICT`
        `GDAL/OGR <http://gdal.org/>`_ is used for getting the proper format.
    `MODE.VERYSTRICT`
        the :class:`lxml.etree` is used along with given input `schema` and the
        GML file is properly validated against given schema.
    """

    LOGGER.info('validating GML; Mode: {}'.format(mode))
    passed = False

    if mode >= MODE.NONE:
        passed = True

    if mode >= MODE.SIMPLE:

        name = data_input.file
        (mtype, encoding) = mimetypes.guess_type(name, strict=False)
        passed = data_input.data_format.mime_type in {mtype, FORMATS.GML.mime_type}

    if mode >= MODE.STRICT:

        from pywps.dependencies import ogr
        data_source = ogr.Open(data_input.file)
        if data_source:
            passed = (data_source.GetDriver().GetName() == "GML")
        else:
            passed = False

    if mode >= MODE.VERYSTRICT:

        from lxml import etree

        try:
            schema_url = data_input.data_format.schema
            gmlschema_doc = etree.parse(urlopen(schema_url))
            gmlschema = etree.XMLSchema(gmlschema_doc)
            passed = gmlschema.validate(etree.parse(data_input.stream))
        except Exception as e:
            LOGGER.warning(e)
            passed = False

    return passed


def validategpx(data_input, mode):
    """GPX validation function

    :param data_input: :class:`ComplexInput`
    :param pywps.validator.mode.MODE mode:

    This function validates GPX input based on given validation mode. Following
    happens, if `mode` parameter is given:

    `MODE.NONE`
        it will return always `True`
    `MODE.SIMPLE`
        the mimetype will be checked
    `MODE.STRICT`
        `GDAL/OGR <http://gdal.org/>`_ is used for getting the proper format.
    `MODE.VERYSTRICT`
        the :class:`lxml.etree` is used along with given input `schema` and the
        GPX file is properly validated against given schema.
    """

    LOGGER.info('validating GPX; Mode: {}'.format(mode))
    passed = False

    if mode >= MODE.NONE:
        passed = True

    if mode >= MODE.SIMPLE:

        name = data_input.file
        (mtype, encoding) = mimetypes.guess_type(name, strict=False)
        passed = data_input.data_format.mime_type in {mtype, FORMATS.GPX.mime_type}

    if mode >= MODE.STRICT:

        from pywps.dependencies import ogr
        data_source = ogr.Open(data_input.file)
        if data_source:
            passed = (data_source.GetDriver().GetName() == "GPX")
        else:
            passed = False

    if mode >= MODE.VERYSTRICT:

        from lxml import etree

        try:
            schema_url = data_input.data_format.schema
            gpxschema_doc = etree.parse(urlopen(schema_url))
            gpxschema = etree.XMLSchema(gpxschema_doc)
            passed = gpxschema.validate(etree.parse(data_input.stream))
        except Exception as e:
            LOGGER.warning(e)
            passed = False

    return passed


def validatexml(data_input, mode):
    """XML validation function

    :param data_input: :class:`ComplexInput`
    :param pywps.validator.mode.MODE mode:

    This function validates XML input based on given validation mode. Following
    happens, if `mode` parameter is given:

    `MODE.NONE`
        it will return always `True`
    `MODE.SIMPLE`
        the mimetype will be checked
    `MODE.STRICT` and `MODE.VERYSTRICT`
        the :class:`lxml.etree` is used along with given input `schema` and the
        XML file is properly validated against given schema.
    """

    LOGGER.info('validating XML; Mode: {}'.format(mode))
    passed = False

    if mode >= MODE.NONE:
        passed = True

    if mode >= MODE.SIMPLE:

        name = data_input.file
        (mtype, encoding) = mimetypes.guess_type(name, strict=False)
        passed = data_input.data_format.mime_type in {mtype, FORMATS.GML.mime_type}

    if mode >= MODE.STRICT:
        from lxml import etree

        # TODO: Raise the actual validation exception to make it easier to spot the error.
        #  xml = etree.parse(data_input.file)
        #  schema.assertValid(xml)
        try:
            fn = os.path.join(_get_schemas_home(), data_input.data_format.schema)
            schema_doc = etree.parse(fn)
            schema = etree.XMLSchema(schema_doc)
            passed = schema.validate(etree.parse(data_input.file))
        except Exception as e:
            LOGGER.warning(e)
            passed = False

    return passed


def validatejson(data_input, mode):
    """JSON validation function

    :param data_input: :class:`ComplexInput`
    :param pywps.validator.mode.MODE mode:

    This function validates JSON input based on given validation mode. Following
    happens, if `mode` parameter is given:

    `MODE.NONE`
        No validation, returns `True`.
    `MODE.SIMPLE`
        Returns `True` if the mime type is correct.
    `MODE.STRICT`
        Returns `True` if the content can be interpreted as a json object.
    """

    LOGGER.info('validating JSON; Mode: {}'.format(mode))
    passed = False

    if mode >= MODE.NONE:
        passed = True

    if mode >= MODE.SIMPLE:

        name = data_input.file
        (mtype, encoding) = mimetypes.guess_type(name, strict=False)
        passed = data_input.data_format.mime_type in {mtype, FORMATS.JSON.mime_type}

    if mode >= MODE.STRICT:

        import json
        try:
            with open(data_input.file) as f:
                json.load(f)
            passed = True

        except ValueError:
            passed = False

    return passed


def validategeojson(data_input, mode):
    """GeoJSON validation example

    >>> import StringIO
    >>> class FakeInput(object):
    ...     json = open('point.geojson','w')
    ...     json.write('''{"type":"Feature", "properties":{}, "geometry":{"type":"Point", "coordinates":[8.5781228542328, 22.87500500679]}, "crs":{"type":"name", "properties":{"name":"urn:ogc:def:crs:OGC:1.3:CRS84"}}}''')  # noqa
    ...     json.close()
    ...     file = 'point.geojson'
    >>> class fake_data_format(object):
    ...     mimetype = 'application/geojson'
    >>> fake_input = FakeInput()
    >>> fake_input.data_format = fake_data_format()
    >>> validategeojson(fake_input, MODE.SIMPLE)
    True
    """

    LOGGER.info('validating GeoJSON; Mode: {}'.format(mode))
    passed = False

    if mode >= MODE.NONE:
        passed = True

    if mode >= MODE.SIMPLE:

        name = data_input.file
        (mtype, encoding) = mimetypes.guess_type(name, strict=False)
        passed = data_input.data_format.mime_type in {mtype, FORMATS.GEOJSON.mime_type}

    if mode >= MODE.STRICT:

        from pywps.dependencies import ogr
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

        with open(base_schema) as fh:
            geojson_base = json.load(fh)

        with open(os.path.join(schema_home, "crs.json")) as fh:
            crs_json = json.load(fh)

        with open(os.path.join(schema_home, "bbox.json")) as fh:
            bbox_json = json.load(fh)

        with open(os.path.join(schema_home, "geometry.json")) as fh:
            geometry_json = json.load(fh)

        cached_json = {
            "http://json-schema.org/geojson/crs.json": crs_json,
            "http://json-schema.org/geojson/bbox.json": bbox_json,
            "http://json-schema.org/geojson/geometry.json": geometry_json
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

    LOGGER.info('validating Shapefile; Mode: {}'.format(mode))
    passed = False

    if mode >= MODE.NONE:
        passed = True

    if mode >= MODE.SIMPLE:

        name = data_input.file
        (mtype, encoding) = mimetypes.guess_type(name, strict=False)
        passed = data_input.data_format.mime_type in {mtype, FORMATS.SHP.mime_type}

    if mode >= MODE.STRICT:

        from pywps.dependencies import ogr

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


def validategeotiff(data_input, mode):
    """GeoTIFF validation example
    """

    LOGGER.info('Validating Shapefile; Mode: {}'.format(mode))
    passed = False

    if mode >= MODE.NONE:
        passed = True

    if mode >= MODE.SIMPLE:

        name = data_input.file
        (mtype, encoding) = mimetypes.guess_type(name, strict=False)
        passed = data_input.data_format.mime_type in {mtype, FORMATS.GEOTIFF.mime_type}

    if mode >= MODE.STRICT:

        try:
            from pywps.dependencies import gdal
            data_source = gdal.Open(data_input.file)
            passed = (data_source.GetDriver().ShortName == "GTiff")
        except ImportError:
            passed = False

    return passed


def validatenetcdf(data_input, mode):
    """netCDF validation.
    """

    LOGGER.info('Validating netCDF; Mode: {}'.format(mode))
    passed = False

    if mode >= MODE.NONE:
        passed = True

    if mode >= MODE.SIMPLE:

        name = data_input.file
        (mtype, encoding) = mimetypes.guess_type(name, strict=False)
        passed = data_input.data_format.mime_type in {mtype, FORMATS.NETCDF.mime_type}

    if mode >= MODE.STRICT:

        try:
            from pywps.dependencies import netCDF4 as nc
            nc.Dataset(data_input.file)
            passed = True
        except ImportError as e:
            passed = False
            LOGGER.exception("ImportError while validating netCDF4 file {}:\n {}".format(data_input.file, e))
        except IOError as e:
            passed = False
            LOGGER.exception("IOError while validating netCDF4 file {}:\n {}".format(data_input.file, e))

    return passed


def validatedods(data_input, mode):
    """OPeNDAP validation.
        """

    LOGGER.info('Validating OPeNDAP; Mode: {}'.format(mode))
    passed = False

    if mode >= MODE.NONE:
        passed = True

    if mode >= MODE.SIMPLE:
        name = data_input.url
        (mtype, encoding) = mimetypes.guess_type(name, strict=False)
        passed = data_input.data_format.mime_type in {mtype, FORMATS.DODS.mime_type}

    if mode >= MODE.STRICT:

        try:
            from pywps.dependencies import netCDF4 as nc
            nc.Dataset(data_input.url)
            passed = True
        except ImportError as e:
            passed = False
            LOGGER.exception("ImportError while validating OPeNDAP link {}:\n {}".format(data_input.url, e))
        except IOError as e:
            passed = False
            LOGGER.exception("IOError while validating OPeNDAP link {}:\n {}".format(data_input.url, e))

    return passed


def _get_schemas_home():
    """Get path to schemas directory
    """
    schema_dir = os.path.join(
        os.path.abspath(
            os.path.dirname(__file__)
        ),
        os.path.pardir,
        "schemas")
    LOGGER.debug('Schemas directory: {}'.format(schema_dir))
    return schema_dir


if __name__ == "__main__":
    import doctest

    from pywps.wpsserver import temp_dir

    with temp_dir() as tmp:
        os.chdir(tmp)
        doctest.testmod()
