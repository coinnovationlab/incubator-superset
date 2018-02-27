""" The keys configured here override those in the default Superset config.py file. The directory were this file is placed must be added to your PYTHONPATH environment variable. Commented keys are parameters you may want to change.
"""
from flask_appbuilder.security.manager import AUTH_DB,AUTH_OAUTH
import sys
import os
# Import custom extension of SecurityManager
from sco_security_manager import AACSecurityManager
CUSTOM_SECURITY_MANAGER = AACSecurityManager

#SECRET_KEY = '\2\1thisismyscretkey\1\2\e\y\y\h' # your app secret key
#SUPERSET_WEBSERVER_PORT = 8088

# SQLAlchemy connection string, i.e., path to the database were you want Superset to store metadata
#SQLALCHEMY_DATABASE_URI = 'sqlite:////path/to/superset.db
#SQLALCHEMY_DATABASE_URI = 'mysql://myapp@localhost/myapp'
#SQLALCHEMY_DATABASE_URI = 'postgresql://root:password@localhost/myapp'

# ----------------------------------------------------
# Authentication config for OAuth2
# ----------------------------------------------------
#AUTH_TYPE = AUTH_OAUTH
AUTH_TYPE = AUTH_DB

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1' #avoids using https
AAC_USER_PROFILE_ENDPOINT = 'https://localhost:8243/aacprofile/1.0.0/basicprofile/me'
AAC_USER_ROLES_ENDPOINT = 'https://localhost:8243/aacroles/1.0.0/userroles/me'
AAC_DASHBOARD_CONTEXT = 'sco.dashboard'
AAC_ROLE_PREFIX = 'dash_'
TENANT_ROLE_PREFIX = 'tenant_'
PROVIDER_ROLE = 'PROVIDER'

OAUTH_PROVIDERS = [
    {'name': 'aac', 'icon': 'fa-google', 'token_key': 'access_token',
        'remote_app': {
            'consumer_key': 'e294bd92-1189-4057-8336-49d9600477bf',
            'consumer_secret': 'b9d8c88b-17e7-40bc-9107-59110a610753',
            'base_url': 'http://localhost:8080/aac/resources/token', #not used?
            'request_token_params': {
              'scope': 'profile.basicprofile.me user.roles.me'
            },
            'request_token_url': None, #leave it None
            'access_token_url': 'http://localhost:8080/aac/oauth/token',
            'authorize_url': 'http://localhost:8080/aac/eauth/authorize'}
    }
]

# Will allow user self registration (necessary for OAuth2)
AUTH_USER_REGISTRATION = True

# The default user self registration role
AUTH_USER_REGISTRATION_ROLE = "Gamma"
