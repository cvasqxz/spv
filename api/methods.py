def hello(environ, start_response):

    data = str("hola").encode()

    response_headers = [
        ('Content-type', 'application/json'),
        ('Content-Length', len(data))
    ]
    start_response('200 OK', response_headers)
    return [data]