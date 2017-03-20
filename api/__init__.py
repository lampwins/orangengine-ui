#!/usr/bin/env python
# Copyright (c) 2016 Jonathan Yantis
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# pylint: disable C0103
#
"""
Flask API Server
"""
import sys
import os
import re
import logging
from logging.handlers import RotatingFileHandler
import configparser
from flask import Flask, jsonify, request, g, make_response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_bcrypt import Bcrypt
from api.utils import OEUIJSONEncoder
from celery import Celery
import redis

logger = logging.getLogger(__name__)

# Populated from config file
debug = 1

# Logging Configuration, default level INFO
logger = logging.getLogger('')
logger.setLevel(logging.INFO)
lformat = logging.Formatter('%(asctime)s %(name)s:%(levelname)s: %(message)s')

# Debug mode Enabled
if debug:
    logger.setLevel(logging.DEBUG)
    logging.debug('Enabled Debug mode')

# Enable logging to file if configured
lfh = RotatingFileHandler("api.log", maxBytes=(1048576*5), backupCount=3)
lfh.setFormatter(lformat)
logger.addHandler(lfh)

# STDOUT Logging defaults to Warning
if not debug:
    lsh = logging.StreamHandler(sys.stdout)
    lsh.setFormatter(lformat)
    lsh.setLevel(logging.WARNING)
    logger.addHandler(lsh)

# Create Flask APP
app = Flask(__name__)
app.config.from_object(__name__)
# database_file = 'sqlite:///' + os.path.join(app.root_path, "api.db")
database = 'postgres://orangengine_ui:orangengine_ui@localhost/orangengine_ui'
app.config.update(dict(
    DATABASE=database,
    SQLALCHEMY_DATABASE_URI=database,
    SECRET_KEY='super sexy secrect key, change me!',
    DEBUG=True,
    BCRYPT_LOG_ROUNDS=4,
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    CELERY_BROKER_URL='redis://localhost:6379/0',
    CELERY_RESULT_BACKEND='redis://localhost:6379/0',
))
app.json_encoder = OEUIJSONEncoder

# encryption module
bcrypt = Bcrypt(app)

# Database module
db = SQLAlchemy(app)

# celery config
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.beat_schedule = {
    'beat_interval_runner': {
        'task': 'api.async.device.beat_interval_runner',
        'schedule': 300.0
    },
}
celery.broker_url = 'redis://localhost:6379/0'
celery.result_backend = 'redis://localhost:6379/0'
celery.conf.timezone = 'UTC'

# redis connections
device_refresh_redis_conection = redis.StrictRedis(host='localhost', port=6379, db=1)
jobs_redis_conection = redis.StrictRedis(host='localhost', port=6379, db=2)

# Safe circular imports per Flask guide
import api.errors
import api.views

# auth blueprint
from api.auth.views import auth_blueprint
app.register_blueprint(auth_blueprint)

from api.async.device import init_devices

@app.before_first_request
def _run_on_start():
    """Lazy init of devices on the first request to the api.
    This should happen pretty early on, for example when a user is authenticating.
    This is okay becasue it is being queued in celery and run in the background.
    """

    logger.debug('Dispatching device init for the first time')
    init_devices.delay()
