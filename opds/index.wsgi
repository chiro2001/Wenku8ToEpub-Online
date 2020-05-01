import sae
from opdsserver import app

application = sae.create_wsgi_app(app)
