from superset import sm
import logging

def clean_test_data():
    """delete all database/datasource views and permissions created for testing purposes, leave only main database and its permissions
    """
    try:
        vm_objects = sm.get_all_view_menu()
        for vm in vm_objects:
            if vm.name.startswith('[') and not vm.name.startswith('[main]'):
                logging.info('Deleting permissions related to: {}'.format(vm))
                #find all permissions related to view-menu object
                pvms = sm.find_permissions_view_menu(vm)
                for pvm in pvms:
                    sm.get_session.delete(pvm)
                sm.get_session.delete(vm)
        sm.get_session.commit()
    except Exception as e:
        logging.error('Error in cleaning up test data: {}'.format(e))

clean_test_data()
