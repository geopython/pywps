"""
Parser parses input parameters, send via HTTP Post or HTTP Get method. If
send via HTTP Post, the input is usually XML file.

Each class in the package is resposible for each type of the request.
"""
__all__ = [
        "GetCapabilities",
        "DescribeProcess",
        "Execute"
        ]
