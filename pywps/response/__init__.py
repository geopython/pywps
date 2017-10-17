from pywps.dblog import update_response
from pywps.response.status import STATUS

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

class WPSResponse(object):

    def __init__(self, wps_request, uuid=None):

        self.wps_request = wps_request
        self.uuid = uuid
        self.message = ''
        self.status = STATUS.NO_STATUS
        self.status_percentage = 0
        self.doc = None

        self.update_status(message="Request accepted", status_percentage=0,
                status=self.status)

    def update_status(self, message=None, status_percentage=None, status=None,
                      clean=True):
        """
        Update status report of currently running process instance

        :param str message: Message you need to share with the client
        :param int status_percentage: Percent done (number betwen <0-100>)
        :param pywps.app.WPSResponse.STATUS status: process status - user should usually
            ommit this parameter
        """

        if message:
            self.message = message

        if status:
            self.status = status

        if status_percentage:
            self.status_percentage = status_percentage

        update_response(self.uuid, self)

    def get_response_doc(self):
        try:
            self.doc = self._construct_doc()
        except Exception as e:
            if hasattr(e, "description"):
                msg = e.description
            else:
                msg = e
            self.update_status(message=msg,
                    status_percentage=100,
                    status=STATUS.ERROR_STATUS)
            raise e

        else:
            self.update_status(message="Response generated",
                    status_percentage=100,
                    status=STATUS.DONE_STATUS)

            return self.doc

