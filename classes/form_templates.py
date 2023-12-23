from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError

class ConnectionForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(),
        Email()
    ])
    

class SignUpFormUser(FlaskForm):

    firstname = StringField('Firstname', validators=[
        DataRequired(),
        Length(min=5, max=15)
        ])

    lastname = StringField('Lastname', validators=[
        DataRequired(),
        Length(min=5, max=15)
        ])
    
    email = StringField('Email', validators=[
        DataRequired(),
        Email()
    ])

    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=5, max=20)
    ])

    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])

    profile_picture = FileField('Profile Picture')

    submit = SubmitField('Sign Up')


class SignUpFormDriver(FlaskForm):

    firstname = StringField('Firstname', validators=[
        DataRequired(),
        Length(min=5, max=15)
        ])

    lastname = StringField('Lastname', validators=[
        DataRequired(),
        Length(min=5, max=15)
        ])
    
    email = StringField('Email', validators=[
        DataRequired(),
        Email()
    ])

    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=5, max=20)
    ])

    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])

    profile_picture = FileField('Profile Picture')

    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        if email.data in self.existing_emails:
            raise ValidationError('This email address is already registered with an account!')


class LogInForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=5, max=15)
        ])
    
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=5, max=20)
    ])

    submit = SubmitField('Log In')


class OtpForm(FlaskForm):
    number1 = StringField('Number 1', validators=[
        DataRequired(),
        Length(min=1,max=1),
    ])

    number2 = StringField('Number 2', validators=[
        DataRequired(),
        Length(min=1,max=1),
    ])


    number3 = StringField('Number 3', validators=[
            DataRequired(),
            Length(min=1,max=1),
        ])


    number4 = StringField('Number 4', validators=[
            DataRequired(),
            Length(min=1,max=1),
        ])
    
    verify = SubmitField('Verify')
    
    def validate(self):
        otp = f"{self.number1.data}{self.number2.data}{self.number3.data}{self.number4.data}"

        if not otp.isdigit() or len(otp) != 4:
            self.number1.errors.append('Invalid OTP format')
            return False
        return True



# class CreateRecipe(FlaskForm):
#     title = StringField('Title', validators=[DataRequired(), Length(min=5, max=50)])
#     content = TextAreaField('Content', validators=[DataRequired(), Length(min=5, max=265)])
#     recipe_image = FileField('Image')

#     submit = SubmitField('Post')

# class EditRecipe(FlaskForm):
#     content = StringField('Content', validators=[DataRequired(), Length(min=5, max=265)])
#     recipe_image = FileField('recipe_image')

#     submit = SubmitField('Edit')
