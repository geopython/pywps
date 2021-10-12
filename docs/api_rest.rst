.. _api_rest:

###################
PyWPS Rest API Doc
###################

Since version 4.5, PyWPS includes an experimental implementation of the novel OGC API.
This standard defines the OGC API - Processes API standard.
This standard builds on the OGC Web Processing Service (WPS) 2.0 Standard
and defines the processing interface to communicate over a RESTful protocol using JSON encodings.

For more details about the standard please refer to https://github.com/opengeospatial/ogcapi-processes

Defining the input/output format (JSON or XML)
================================================

WPS 1.0 standard defines input and outputs in XML format.
OGC API - Processes: rest-api, json.
PyWPS >= 4.5 allows inputs and outputs to be in both XML and JSON formats.

The default format (mimetype) of the input/output is determinate by the URL:

* Default XML - if the url starts with `/wps`
* Default JSON - if the url starts with `/jobs` or `/processes`

Please refer to `app.basic.parse_http_url` for full details about those defaults.


GET request:
-------------

The default mimetype (output format) can be set by adding `&f=json` or `&f=xml` parameter.

GET GetCapabilities Request URL:

.. code-block:: json

    http://localhost:5000/processes/?service=WPS
    http://localhost:5000/wps/?request=GetCapabilities&service=WPS&f=json

GET GetCapabilities Response:

.. code-block:: json

    {
      "pywps_version": "4.5.0",
      "version": "1.0.0",
      "title": "PyWPS WPS server",
      "abstract": "PyWPS WPS server server.",
      "keywords": [
        "WPS",
        "PyWPS",
      ],
      "provider": {
        "name": "PyWPS Development team",
        "site": "https://github.com/geopython/pywps-flask",
      },
      "serviceurl": "http://localhost:5000/wps",
      "languages": [
        "en-US"
      ],
      "language": "en-US",
      "processes": [
        {
          "class": "processes.sayhello:SayHello",
          "uuid": "None",
          "workdir": null,
          "version": "1.3.3.8",
          "identifier": "say_hello",
          "title": "Process Say Hello",
          "abstract": "Returns a literal string output with Hello plus the inputed name",
          "keywords": [],
          "metadata": [],
          "inputs": [
            {
              "identifier": "name",
              "title": "Input name",
              "abstract": "",
              "keywords": [],
              "metadata": [],
              "type": "literal",
              "data_type": "string",
              "workdir": null,
              "allowed_values": [],
              "any_value": false,
              "mode": 1,
              "min_occurs": 1,
              "max_occurs": 1,
              "translations": null,
              "data": "World"
            }
          ],
          "outputs": [
            {
              "identifier": "output",
              "title": "Output response",
              "abstract": "",
              "keywords": [],
              "data": null,
              "data_type": "string",
              "type": "literal",
              "uoms": [],
              "translations": null
            }
          ],
          "store_supported": "true",
          "status_supported": "true",
          "profile": [],
          "translations": null
        }
      ]
    }

GET DescribeProcess Request URL:

.. code-block:: json

    http://localhost:5000/processes/say_hello?service=WPS
    http://localhost:5000/wps/?request=DescribeProcess&service=WPS&identifier=say_hello&version=1.0.0&f=json

GET DescribeProcess Response:

.. code-block:: json

    {
      "pywps_version": "4.5.0",
      "processes": [
        {
          "class": "processes.sayhello:SayHello",
          "uuid": "None",
          "workdir": null,
          "version": "1.3.3.8",
          "identifier": "say_hello",
          "title": "Process Say Hello",
          "abstract": "Returns a literal string output with Hello plus the inputed name",
          "keywords": [],
          "metadata": [],
          "inputs": [
            {
              "identifier": "name",
              "title": "Input name",
              "abstract": "",
              "keywords": [],
              "metadata": [],
              "type": "literal",
              "data_type": "string",
              "workdir": null,
              "allowed_values": [],
              "any_value": false,
              "mode": 1,
              "min_occurs": 1,
              "max_occurs": 1,
              "translations": null,
              "data": "World"
            }
          ],
          "outputs": [
            {
              "identifier": "output",
              "title": "Output response",
              "abstract": "",
              "keywords": [],
              "data": null,
              "data_type": "string",
              "type": "literal",
              "uoms": [],
              "translations": null
            }
          ],
          "store_supported": "true",
          "status_supported": "true",
          "profile": [],
          "translations": null
        }
      ],
      "language": "en-US"
    }

GET Execute Request URL:

.. code-block:: json

    http://localhost:5000/wps?/service=wps&version=1.0.0&request=execute&Identifier=say_hello&storeExecuteResponse=true&DataInputs=name=Dude&f=json

GET Execute Response:

.. code-block:: json

    {
        "status": {
            "status": "succeeded",
            "time": "2021-06-15T14:19:28Z",
            "percent_done": "100",
            "message": "PyWPS Process Process Say Hello finished"
        },
        "outputs": {
            "output": "Hello Dude"
        }
    }

GET Execute Request URL (Raw output):

.. code-block:: json

    http://localhost:5000/wps?/service=wps&version=1.0.0&request=execute&Identifier=say_hello&storeExecuteResponse=true&DataInputs=name=Dude&RawDataOutput=output

GET Execute Response:

.. code-block:: json

    Hello Dude


POST request:
---------------

The default mimetype (input and output formats) can be changed by setting the following headers
of a POST request to one following values `text/xml` or `application/json`:

    * `Content-Type` (format of the input)
    * `Accept` (format of the output)

Example of a `Say Hello` POST request:

POST Execute Request URL:

.. code-block:: json

    http://localhost:5000/jobs

POST Execute Request Body:

.. code-block:: json

    {
        "identifier": "say_hello",
        "inputs": {
            "name": "Dude"
        }
    }

POST Execute Response:

.. code-block:: json

    {
        "status": {
            "status": "succeeded",
            "time": "2021-06-15T14:19:28Z",
            "percent_done": "100",
            "message": "PyWPS Process Process Say Hello finished"
        },
        "outputs": {
            "output": "Hello Dude"
        }
    }


Example of a `Say Hello` POST request with raw output:

POST Execute Request Body:

.. code-block:: json

    {
        "identifier": "say_hello",
        "outputs": "output",
        "inputs": {
            "name": "Dude"
        }
    }


POST Execute Response:

.. code-block:: json

    Hello Dude

Alternatively, the `identifier` and optionally the raw output name can be encoded in the Request URL:

POST Execute Request URL (with `identifier`):

.. code-block:: json

    http://localhost:5000/jobs/say_hello

POST Execute Request Body:

.. code-block:: json

    {
        "name": "Dude"
    }

POST Execute Response:

.. code-block:: json

    {
        "status": {
            "status": "succeeded",
            "time": "2021-06-15T14:19:28Z",
            "percent_done": "100",
            "message": "PyWPS Process Process Say Hello finished"
        },
        "outputs": {
            "output": "Hello Dude"
        }
    }

POST Execute Request URL (with `identifier` and output name):

.. code-block:: json

    http://localhost:5000/jobs/say_hello/output

POST Execute Request Body:

.. code-block:: json

    {
        "name": "Dude"
    }

POST Execute Response:

.. code-block:: json

    Hello Dude


Example for a reference input:

.. code-block:: json

    "raster": {
        "type": "reference",
        "href": "file:./path/to/data/data.tif"
    }

Example for a BoundingBox input:
(bbox default axis order is yx (EPSG:4326), i.e. miny, minx, maxy, maxx)

.. code-block:: json

    "extent": {
        "type": "bbox",
        "bbox": [32, 34.7, 32.1, 34.8]
    }


Example for a ComplexInput input:
(the data is a standard GeoJSON)

.. code-block:: json

    "cutline": {
        "type": "complex",
        "data": {
            "type": "FeatureCollection",
            "name": "Center",
            "crs": {
                "type": "name",
                "properties": {
                    "name": "urn:ogc:def:crs:OGC:1.3:CRS84"
                }
            },
            "features": [
                {
                    "type": "Feature",
                    "properties": {},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [
                                    34.76844787397541,
                                    32.07247233606565
                                ],
                                [
                                    34.78658619364754,
                                    32.07260143442631
                                ],
                                [
                                    34.77780750512295,
                                    32.09532274590172
                                ],
                                [
                                    34.76844787397541,
                                    32.07247233606565
                                ]
                            ]
                        ]
                    }
                }
            ]
        }
    }


The examples above show some `Literal`, 'Complex', `BoundingBox` inputs.
Internally, PyWPS always keeps the inputs in JSON formats (also in previous versions)
So potentially all input types that are supported in XML should also be supported in JSON,
though only a small subset of them were tested in this preliminary implementation.

Multiple inputs for the same parameter can be passed by using a list as the parameter value.
