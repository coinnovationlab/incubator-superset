PREREQUISITES:
- Python 2.7 or 3.4

0. (Optional but recommended) Create a virtual environment and install everything there (`virtualenv` comes by default with Python 3.4, must be installed with 2.7):

`virtualenv myenv`

`source myenv\bin\activate`

1. Get source code:

`git clone https://github.com/coinnovationlab/incubator-superset.git`

`cd incubator-superset`

`git checkout 0.22.1-sco`

2. Install Node.js and Yarn (instructions taken from "https://www.digitalocean.com/community/tutorials/how-to-install-nodejs-on-ubuntu-16-04" and "https://yarnpkg.com/lang/en/docs/install/", work for Ubuntu 16.04, not tested on other versions):

`curl -sL https://deb.nodesource.com/setup_6.x -o nodesource_setup.sh`

`sudo bash nodesource_setup.sh`

`sudo apt-get install nodejs`

`curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -`

`echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list`

`sudo apt update`

`sudo apt install yarn`

`sudo apt install nodejs-legacy`

3. Install OS dependencies (from Superset documentation):

`sudo apt install build-essential libssl-dev libffi-dev python-dev python-pip libsasl2-dev libldap2-dev`

4. Set dependencies:

`cd .../incubator-superset/superset/assets`
`yarn`

(`npm run sync-backend` may be necessary only during development; try first skipping this line)

`yarn run build`

5. Install Flask-Oauthlib, i.e. Flask library for OAuth2:

`pip install Flask-OAuthlib`

6. Install and launch Superset (from "https://superset.incubator.apache.org/installation.html"):

`cd .../incubator-superset`

`python setup.py install` or `pip install .`

`fabmanager create-admin --app superset`

`superset db upgrade`

`superset init`

(`superset load_examples` optional, loads some sample datasources, slices and dashboards)

`superset runserver`

7. Now you have Superset running with its default configuration and username-password authentication. The config file and the custom security manager that shall however be used from now on are in "incubator-superset/sco_configuration" folder, therefore the path to this folder must be addedd to your PYTHONPATH env variable, e.g. by adding the following at the end of your ~/.bashrc file:

`PYTHONPATH="${PYTHONPATH}:/path/to/incubator-superset/sco_configuration/"`

`export PYTHONPATH`

DATABASE DEPENDENCIES:
In order to configure Superset connection with your databases of choice, you need to install the corresponding packages. See `https://superset.incubator.apache.org/installation.html#database-dependencies` for further instructions.

AUTHENTICATION WITH OAuth2:
1. Make sure that authentication type in "incubator-superset/sco\_configuration/superset\_config.py" is set as follows: `AUTH_TYPE = AUTH_OAUTH`

2. Create a provider in AAC:
- Log in to AAC as admin and create a new provider (e.g. with domain `sco.dashboard`)
- Log in to WSO2 store as the newly created provider, enter domain `sco.dashboard` and create a new application (e.g. `SupersetClient`). Generate production keys and add the callback URLs (change Superset host and port if needed): `http://localhost:8088/oauth-authorized/aac,http://localhost:8088/oauth-authorized/aac/` . Enter `carbon.super` domain and subscribe to AAC and AACRoles APIs with the new application.
- Log in to AAC as the provider and change these settings for the new application:
  - Grant Types: all
  - Enabled identity providers: internal (approve this setting as admin from the "Admin" tab)
  - In API Access tab, basic profile service: profile.basicprofile.me
  - Role management service: user.roles.me

3. Configure OAUTH_PROVIDERS in "incubator-superset/sco\_configuration/superset\_config.py":
- consumer_key: the consumer key (or clientId) you generated for the application
- consumer_secret: the client secret you generated
- check that host and port in the URLs match those you are using for AAC

4. Notice the following properties in superset_config.py. You can change them if needed:

- AAC\_USER\_PROFILE\_ENDPOINT = 'https://localhost:8243/aacprofile/1.0.0/basicprofile/me'
- AAC\_USER\_ROLES\_ENDPOINT = 'https://localhost:8243/aacroles/1.0.0/userroles/me'
- AAC\_DASHBOARD\_CONTEXT = 'sco.dashboard'       #must match the name of the domain you created in AAC
- AAC\_ROLE\_PREFIX = 'dash\_'                    #role prefix expected for AAC users that are owners of an organization; AAC users with role <AAC_ROLE_PREFIX><org_name> will have role <TENANT_ROLE_PREFIX><org_name> in Superset
- TENANT\_ROLE\_PREFIX = 'tenant_'                #role prefix that Superset will give to AAC users that are owners of an organization
- PROVIDER\_ROLE = 'PROVIDER'                     #role of domain provider; a user that is provider of AAC\_DASHBOARD\_CONTEXT will have admin role in Superset
