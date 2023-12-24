from flask import Blueprint, render_template, request, redirect, send_file
from flask_login import current_user
from services.driver_services import get_unverified_drivers, get_driver_document, approve_driver, reject_driver
from services.performance_services import route_list, get_performance_content
from database.MongoDB.mongo import client
from cache.cache_setup import cache

admin_blueprint = Blueprint('admin', __name__)
db = client['Quickie']
rides = db['rides']


# Admin Middleware
@admin_blueprint.before_request
def before_request():
    if current_user.is_anonymous:
        return redirect('/connection')
    if current_user.role != 'admin':
        return redirect('/home')
            
    if request.path != '/admin/performance' and request.path != '/admin/drivers':
        return redirect('/admin/performance')
    

# Redirecting to admin dashboard
@admin_blueprint.route('/', methods=['GET'])
def index():
    return redirect('/admin/performance')


# Admin Dashboard with performance and driver approval sections
@admin_blueprint.route('/<section>', methods=['GET'])
def information(section):
    if section == 'drivers':
        unverified_drivers  = get_unverified_drivers()
        return render_template('admin.html', user=current_user, drivers=unverified_drivers, section=section)
    elif section == 'performance':
        if cache.get(f'routes'):
            routes = cache.get('routes')
            print('routes from cache')
        else:
            routes = route_list()
            cache.set('routes',routes)
            print('routes from db')

        performance_content = get_performance_content()
        print(performance_content)
    return render_template('admin.html', user=current_user, routes=routes, section=section, logs=performance_content)


# Downloading driver documents
@admin_blueprint.route('/download/<driver_id>/<document_name>', methods=['GET'])
def download(driver_id,document_name):
    document = get_driver_document(driver_id, document_name)
    return send_file(document, as_attachment=True, download_name=f'{document_name}-{driver_id}')


# Approving a driver
@admin_blueprint.route('/approve/<driver_id>', methods=['POST'])
def approve(driver_id):
    result = approve_driver(driver_id)
    print('result is', result)
    return result

# Rejecting a driver
@admin_blueprint.route('/reject/<driver_id>', methods=['POST'])
def reject(driver_id):
    result = reject_driver(driver_id)
    print('result is', result)
    return result
