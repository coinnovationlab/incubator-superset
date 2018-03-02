import logging
import base64
import requests
import json
from flask import g, url_for, redirect, request, flash, Response
from flask_login import login_user
from flask_appbuilder import const, expose
from flask_appbuilder._compat import as_unicode
from superset import sm, appbuilder
from superset.utils import has_access
from superset.models.core import Dashboard
from superset.views.base import BaseSupersetView, json_error_response

dash_viewonly_url = 'dashboard-viewonly/{d_id}?standalone=true&access_key={key}'

class DashboardSharing(BaseSupersetView):
    @expose('/share-dash/<dashboard_id>', methods=['GET'])
    @has_access
    def share_dash(self, dashboard_id):
        dashboard_obj = sm.get_session.query(Dashboard).filter_by(id=dashboard_id).first()
        
        #create a role for viewers of the dashboard
        rolename = 'dashviewer_{}_{}'.format(dashboard_id, dashboard_obj.dashboard_title)
        role = sm.find_role(rolename)
        if not role:
            role = sm.add_role(rolename)
            logging.info('Role {} created'.format(role))
        sm.add_permission_role(role, sm.find_permission_view_menu('can_dashboard', 'Superset'))
        sm.add_permission_role(role, sm.find_permission_view_menu('can_explore_json', 'Superset'))
        for datasource in dashboard_obj.datasources:
            sm.add_permission_role(role, sm.find_permission_view_menu('datasource_access', datasource.get_perm()))
        
        #create background user with role
        viewername = 'viewer_{}_{}'.format(dashboard_id, dashboard_obj.dashboard_title)
        viewer = sm.find_user(viewername)
        if not viewer:
            viewer = sm.add_user(viewername, '', '', viewername, [role])
        
        #generate access key
        try:
            access_key = base64.encodestring(viewer.username + ':' + viewer.password)
            #TODO add localhost:8088 to url
            auth_url = request.url_root + dash_viewonly_url.format(d_id=dashboard_id, key=access_key)
            return Response(auth_url, status=200)
        except Exception as e:
            return json_error_response(e)

appbuilder.add_view_no_menu(DashboardSharing)

def viewonly_dashboard(dashboard_id):
    #check if user is already authenticated
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('Superset.dashboard', dashboard_id=dashboard_id))
    
    #authenticate user using access key
    access_key = request.args.get('access_key')
    if not access_key:
        return json_error_response('Parameter access_key is missing from the URL', status=400)
    
    try:
        credentials = (base64.decodestring(access_key)).split(':', 1)
    except Exception as e:
        return json_error_response(e)
    
    user = auth_user_db_without_check_password_hash(sm, credentials[0], credentials[1])
    if not user:
        return json_error_response('Access denied. Either the access key provided is incorrect or you do not have sufficient privileges to view this content.', status=401)
    login_user(user, remember=False)
    
    #redirect to dashboard
    return redirect((url_for('Superset.dashboard', dashboard_id=dashboard_id)) + '?standalone=true')

def auth_user_db_without_check_password_hash(sec_manager, username, password):
    """
    Authenticate user against database
    """
    if username is None or username == "":
        return None
    user = sec_manager.find_user(username=username)
    if user is None or (not user.is_active()):
        logging.info(const.LOGMSG_WAR_SEC_LOGIN_FAILED.format(username))
        return None
    if user.password == password:
        sm.update_user_auth_stat(user, True)
        return user
    else:
        sm.update_user_auth_stat(user, False)
        logging.info(const.LOGMSG_WAR_SEC_LOGIN_FAILED.format(username))
        return None


"""
def share_dashboard(dashboard_id):
    dashboard_obj = sm.get_session.query(Dashboard).filter_by(id=dashboard_id).first()
    
    #create a role for viewers of the dashboard
    rolename = 'dashviewer_{}'.format(dashboard_id)
    role = sm.find_role(rolename)
    if not role:
        role = sm.add_role(rolename)
        logging.info('Role {} created'.format(role))
    sm.add_permission_role(role, sm.find_permission_view_menu('can_dashboard', 'Superset'))
    sm.add_permission_role(role, sm.find_permission_view_menu('can_explore_json', 'Superset'))
    for datasource in dashboard_obj.datasources:
        sm.add_permission_role(role, sm.find_permission_view_menu('datasource_access', datasource.get_perm()))
    
    #create background user with role
    viewer = sm.find_user('viewer_{}'.format(dashboard_id))
    if not viewer:
        viewer = sm.add_user('viewer_{}'.format(dashboard_id), '', '', 'viewer_{}'.format(dashboard_id), [role])
    
    #generate access key
    if viewer:
        access_key = base64.encodestring(viewer.username + ':' + viewer.password)
        auth_url = dash_viewonly_url.format(d_id=dashboard_id, key=access_key)
        #TODO user interface, e.g. flask.flash message
        return auth_url
    else:
        #TODO return http 500
        logging.error('Error creating user viewer_{}'.format(dashboard_id))
        return 'Cannot share dashboard. Please contact the admin.'
"""
