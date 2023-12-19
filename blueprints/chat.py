from flask import Blueprint, render_template, request, redirect, flash, url_for, session
from flask_login import login_required, current_user
from services.sqlite_functions import add_user
from services.user_services import add_payment_method
from services.chat_services import add_message, get_messages, create_chat
from database.MongoDB.mongo import client

chat_blueprint = Blueprint('chat', __name__)
db = client['Quickie']
chats = db['chats']

@chat_blueprint.route('/message/create', methods=['POST'])
def create():
    data = request.get_json()
    message = data['message']
    sender = data['sender']
    receiver = data['receiver']
    chat_id = data['chat_id']
    print('sender',sender,'receiver',receiver,'message',message,'chat_id',chat_id)
    result = add_message(sender, receiver,message,chat_id)
    return result

@chat_blueprint.route('/message/getall', methods=['POST'])
def getall():
    data = request.get_json()
    driver = data['driver']
    customer = data['customer']
    chat_id = data['chat_id']
    result = add_message(driver, customer,chat_id)
    return result

