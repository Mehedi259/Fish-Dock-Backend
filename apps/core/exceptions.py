from rest_framework.views import exception_handler
from rest_framework.response import Response

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        custom_data = {
            'success': False,
            'message': 'An error occurred while processing your request.',
            'errors': response.data
        }
        if isinstance(response.data, dict) and 'detail' in response.data:
            custom_data['message'] = str(response.data['detail'])
        response.data = custom_data

    return response

