from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, firstname, lastname, email,role):
         self.id = id
         self.firstname = firstname
         self.lastname = lastname
         self.email = email
         self.role = role
         self.authenticated = False
         self.profile_picture = None  
         
    def get_id(self):
         return self.id
    
    def set_profile_picture(self, profile_picture):
        self.profile_picture = profile_picture