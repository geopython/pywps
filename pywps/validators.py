from abc import ABCMeta, abstractmethod, abstractproperty

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
    >>> fake_input = FakeInput()
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
        passed = bool(mtype)

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
        return gmlschema.validate(etree.parse(open(data_input.file)))

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
