
import logging
from flask import Flask, jsonify, request, g, make_response
from api import app
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)

def standard_responce(data, code):
    if isinstance(data, basestring):
        data = {'error': data}
    elif isinstance(data, HTTPException):
        # origin is an abort()
        data = {'error': data.description}
    message = {
        'status': code,
        'errors': data,
    }
    resp = jsonify(message)
    return resp, code

@app.errorhandler(404)
def not_found(error='The requested resource was not found'):
    return standard_responce(error, 404)

@app.errorhandler(429)
def ratelimit_handler(error="Ratelimit exceeded"):
    return standard_responce(error, 429)

@app.errorhandler(400)
def bad_request(error="Bad request"):
    return standard_responce(error, 400)

@app.errorhandler(501)
def not_implemented(error="Not implemented"):
    return standard_responce(error, 501)

@app.errorhandler(403)
def not_authorized(error="Not authorized"):
    return standard_responce(error, 403)
