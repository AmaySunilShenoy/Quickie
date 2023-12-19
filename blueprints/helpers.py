from flask import Blueprint, render_template, request, redirect, flash, url_for, session
from flask_login import login_required, current_user

from database.MongoDB.mongo import client

helpers_blueprint = Blueprint('helpers', __name__)
db = client['Quickie']
rides = db['rides']

@helpers_blueprint.route('/', methods=['GET'])
@login_required
def index():
    return redirect('/profile/trips')

@helpers_blueprint.route('/<section>', methods=['GET'])
@login_required
def profile_info(section):
    if section not in ['trips', 'wallet', 'settings']:
        return redirect('/profile/trips')
    return render_template('profile.html', user=current_user,section=section)