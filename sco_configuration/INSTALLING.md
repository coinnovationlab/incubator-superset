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

5. Install and launch Superset (from "https://superset.incubator.apache.org/installation.html"):
`cd .../incubator-superset`
`python setup.py install` or `pip install .`
`fabmanager create-admin --app superset`
`superset db upgrade`
`superset init`
(`superset load_examples` optional, loads some sample datasources, slices and dashboards)
`superset runserver`

NOTE: by now Superset is running with its default configuration and username-password authentication. The config file and the custom security manager that shall be used instead are in "incubator-superset/sco_configuration" folder, therefore the path to this folder must be addedd to your PYTHONPATH env variable, e.g. by adding the following at the end of your ~/.bashrc file:
`PYTHONPATH="${PYTHONPATH}:/path/to/incubator-superset/sco_configuration/"`
`export PYTHONPATH`
