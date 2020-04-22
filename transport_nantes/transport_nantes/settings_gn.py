# Settings file for le-grand-nantes.fr.

from transport_nantes.settings import *

SITE_ID = 2

# This is the application object that django's built-in server (i.e.,
# runserver) will use.  In production, this is specified to gunicorn
# on the commandline.
WSGI_APPLICATION = 'transport_nantes.wsgi_gn.application'
