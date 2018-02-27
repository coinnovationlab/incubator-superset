"""
Extension for authentication with AAC
"""
import logging
from flask import g, session
from flask_appbuilder import const as c
from flask_appbuilder.security.sqla.manager import SecurityManager #child of BaseSecurityManager
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_babel import gettext as __
from werkzeug.security import generate_password_hash
import sqlalchemy
import superset_config as conf

class AACSecurityManager(SecurityManager):
    """
    Custom security manager
    """
    _provider = None

    def __init__(self, appbuilder):
        super(AACSecurityManager, self).__init__(appbuilder)
    
    def get_oauth_user_info(self, provider, resp=None):
        """
        Overriding from BaseSecurityManager
        """
        self._provider = self.appbuilder.sm.oauth_remotes[provider]
        #for Google
        if provider == 'google':
            me = self._provider.get('userinfo')
            logging.debug("User info from Google: {0}".format(me.data))
            return {
                'username': "google_" + me.data.get('id', ''),
                'first_name': me.data.get('given_name', ''),
                'last_name': me.data.get('family_name', ''),
                'email': me.data.get('email', '')
            }
        #for AAC
        if provider == 'aac':
            me = self._provider.get(conf.AAC_USER_PROFILE_ENDPOINT, content_type='application/json')
            logging.debug("User info from AAC: {0}".format(me.data))
            return {
                'username': 'aac_' + me.data.get('userId', ''),
                'first_name': me.data.get('name', ''),
                'last_name': me.data.get('surname', ''),
                'email': me.data.get('name', '') + me.data.get('surname', '') + '@email.com'
            }
        else:
            return {}

    def auth_user_oauth(self, userinfo):    
        """
        Overriding from BaseSecurityManager
        """
        if 'username' in userinfo:
            user = self.find_user(username=userinfo['username'])
        elif 'email' in userinfo:
            user = self.find_user(email=userinfo['email'])
        else:
            logging.error('User info does not have username or email {0}'.format(userinfo))
            return None
        # User is disabled
        if user and not user.is_active():
            logging.info(c.LOGMSG_WAR_SEC_LOGIN_FAILED.format(userinfo))
            return None
        # If user does not exist on the DB and not self user registration, go away
        if not user and not self.auth_user_registration:
            return None
        # User does not exist, create one if self registration.
        if not user:
            user = self.add_user(
                username=userinfo['username'],
                first_name=userinfo['first_name'],
                last_name=userinfo['last_name'],
                email=userinfo['email'],
                roles=self.get_mapped_roles() #role=self.find_role(self.auth_user_registration_role)
            )
            if not user:
                logging.error("Error creating a new OAuth user %s" % userinfo['username'])
                return None
        self.update_user_auth_stat(user)
        return user
    
    def add_user(self, username, first_name, last_name, email, roles, password='', hashed_password=''):
        """
        Overriding from BaseSecurityManager to add more than one role
        """
        try:
            user = self.user_model()
            user.first_name = first_name
            user.last_name = last_name
            user.username = username
            user.email = email
            user.active = True
            for role in roles:
                user.roles.append(role)
            if hashed_password:
                user.password = hashed_password
            else:
                user.password = generate_password_hash(password)
            self.get_session.add(user)
            self.get_session.commit()
            logging.info(c.LOGMSG_INF_SEC_ADD_USER.format(username))
            return user
        except Exception as e:
            logging.error(c.LOGMSG_ERR_SEC_ADD_USER.format(str(e)))
            return False

    def get_mapped_roles(self):
        """
        Request AAC roles for the user that tries to authenticate
        {"id": 21,"scope": "application","role": "dash_test1","context": "sco.dashboard","authority": "dash_test1"}
        """
        roles = [self.find_role('Gamma')] #list of roles to be returned
        aac_roles = self._provider.get(conf.AAC_USER_ROLES_ENDPOINT, content_type='application/json')
        logging.debug("User roles from AAC: {0}".format(aac_roles.data))
        
        for role_dict in aac_roles.data:
            if role_dict['role'] == conf.PROVIDER_ROLE and role_dict['context'] and role_dict['context'] == conf.AAC_DASHBOARD_CONTEXT:
                roles.append(self.find_role('Admin'))
            elif role_dict['role'].startswith(conf.AAC_ROLE_PREFIX) and role_dict['context'] and role_dict['context'] == conf.AAC_DASHBOARD_CONTEXT:
                #slice to take tenant name
                org = role_dict['role'][len(conf.AAC_ROLE_PREFIX):]
                
                tenant_role = self.find_role(conf.TENANT_ROLE_PREFIX + org)
                if not tenant_role:
                    tenant_role = self.add_role(conf.TENANT_ROLE_PREFIX + org)
                    logging.debug("Role {0} created".format(tenant_role))
                    #add permissions to manage data
                    self.add_permission_role(tenant_role, self.find_permission_view_menu('can_add', 'DatabaseView'))
                    self.add_permission_role(tenant_role, self.find_permission_view_menu('can_edit', 'DatabaseView'))
                    self.add_permission_role(tenant_role, self.find_permission_view_menu('can_add', 'TableModelView'))
                    self.add_permission_role(tenant_role, self.find_permission_view_menu('can_edit', 'TableModelView'))
                    logging.debug("Role has permissions: {0}".format(tenant_role.permissions))
                roles.append(tenant_role)
        return roles


