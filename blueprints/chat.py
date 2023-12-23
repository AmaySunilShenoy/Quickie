from flask import Blueprint, request
import time
from services.chat_services import add_message
from database.MongoDB.mongo import client
from loggers.loggers import performance_logger, action_logger
chat_blueprint = Blueprint('chat', __name__)
db = client['Quickie']
chats = db['chats']


# Creating a new Message
@chat_blueprint.route('/message/create', methods=['POST'])
def create():
    start_time = time.time()
    data = request.get_json()
    message = data['message']
    sender = data['sender']
    receiver = data['receiver']
    chat_id = data['chat_id']
    print('sender',sender,'receiver',receiver,'message',message,'chat_id',chat_id)
    result = add_message(sender, receiver,message,chat_id)
    end_time = time.time()
    performance_logger.info(f'Route - /message/create loaded in {(end_time - start_time) : .3f} seconds')
    action_logger.info(f'User {sender} sent a message to {receiver}')
    return result