
from api import app as api_app
from frontend import app as frontend_app
from werkzeug.wsgi import DispatcherMiddleware
from werkzeug.serving import run_simple


application = DispatcherMiddleware(
    frontend_app,
    {
        '/api': api_app
    }
)

run_simple("localhost", 5000, application)
