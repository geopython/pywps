from lxml import etree as _etree


PARSER = _etree.XMLParser(
    resolve_entities=False,
)

tostring = _etree.tostring


def fromstring(text):
    return _etree.fromstring(text, parser=PARSER)


def parse(source):
    return _etree.parse(source, parser=PARSER)
