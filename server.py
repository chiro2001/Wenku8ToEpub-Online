import os
from flask import *
from flask_cors import *
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple

from manage import app
from opds.opdsserver import app as app_opds

# app = Flask(__name__)

CORS(app, supports_credentials=True)

dm = DispatcherMiddleware(app,
    {
        '/opds': app_opds
    }
)


if __name__ == '__main__':
    # app.run("0.0.0.0", port=int(os.environ.get('PORT', '8000')), debug=False)
    run_simple('0.0.0.0', int(os.environ.get('PORT', '8000')), dm)