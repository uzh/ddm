from ddm.models.exceptions import *
from rest_framework.views import APIView


class ExceptionAPI(APIView):

    def get(self, request, format=None, *args, **kwargs):
        """
        Return a dictionary object containing the error message.

        The following variables must be supplied with an API query:
        - status_code: The code identifier of the raised exception
        - project_id: The identifier of the project in which the exception was encountered
        - participant_id: The id of the participant that encountered the exception
        """
        # Authenticate request somehow; e.g.: ensure that project and participant exist in db - seems unsure though

        # Get requested exception class.
        exception_code = self.kwargs.get('status_code', None)
        exception_class = DDM_EXCEPTIONS.get(exception_code, DDMBaseException)

        # Register the error on server side. (async?)
        # register_exception(exception_class)
        # or:
        # exception_class.register_with_project(project_id)

        # Return exception information to vue.
        excpetion_information = {
            'description': exception_class.description,
            'message': exception_class.message
        }
        return excpetion_information
