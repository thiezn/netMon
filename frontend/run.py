#!/usr/bin/env python3

from app import dbinit
from os import environ
from app import app

if __name__ == '__main__':

    dbinit()

    HOST = environ.get('SERVER_HOST', '0.0.0.0')
    try:
        PORT = int(environ.get('SERVER_PORT', '8080'))
    except ValueError:
        PORT = 8080
    app.run(HOST, PORT, debug=True)
