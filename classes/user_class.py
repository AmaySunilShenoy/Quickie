from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, firstname, lastname, email,role):
         self.id = id
         self.firstname = firstname
         self.lastname = lastname
         self.email = email
         self.role = role
         self.authenticated = False   
         
    def get_id(self):
         return self.id