

def get_response(operation):

    from .capabilities import CapabilitiesResponse
    from .describe import DescribeResponse

    if operation == "capabilities":
        return CapabilitiesResponse
    elif operation == "describe":
        return DescribeResponse
