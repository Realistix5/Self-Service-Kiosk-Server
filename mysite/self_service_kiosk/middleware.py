import logging


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        logger = logging.getLogger('request_logger')

        # Default values in case decoding fails
        headers = dict(request.headers)

        try:
            body = request.body.decode('utf-8')
        except UnicodeDecodeError:
            body = '<decoding error>'

        logger.info('Request: %s %s, Payload: %s, Headers: %s', request.method, request.get_full_path(), body, headers)

        response = self.get_response(request)
        return response
