from database.MongoDB.mongo import client
from datetime import datetime
db = client['Quickie']
messages = db['messages']
chats = db['chats']

def create_chat(driver, customer, ride_id):
    existing_chat = chats.find_one({'driver':driver, 'customer':customer, 'ride_id':ride_id})
    if not existing_chat:
        chat = {'driver':driver, 'customer':customer, 'ride_id':ride_id, 'created_at':datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
        result = chats.insert_one(chat)
        return result.inserted_id
    else:
        return existing_chat['_id']

def add_message(sender_id, receiver_id, message, chat_id):
    try:
        result = messages.insert_one({'sender_id': sender_id, 'receiver_id': receiver_id, 'message': message, 'chat_id': chat_id, 'created_at':datetime.now().strftime("%d/%m/%Y %H:%M:%S")})
        if result:
            return {'status': 'success'}
        else:
            return {'status': 'error'}
    except Exception as e:
        print("Error in add_message:", e)
        return {'status': 'error'}
    

def get_messages(chat_id):
    result = messages.find({'chat_id': chat_id})
    return result