

def get_response(operation):

    from .capabilities import CapabilitiesResponse
    from .describe import DescribeResponse
    from .execute import ExecuteResponse

    if operation == "capabilities":
        return CapabilitiesResponse
    elif operation == "describe":
        return DescribeResponse
    elif operation == "execute":
        return ExecuteResponse
