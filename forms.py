from flask import Flask
from flask_pymongo import PyMongo
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField , DateField
from wtforms.validators import InputRequired, Length, ValidationError
import secrets

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/seconddb'
app.config['SECRET_KEY'] = secrets.token_hex(16)

mongo = PyMongo(app)


#the registre form (wch lazem t3mr kamel)
class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=8, max=16)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=16)], render_kw={"placeholder": "Password"})
    birthdate = DateField('Birthdate', format='%Y-%m-%d', validators=[InputRequired()], render_kw={"placeholder": "YYYY-MM-DD"})
    name = StringField(validators=[InputRequired(), Length(min=2 , max=20)], render_kw={"placeholder":"Name"})
    submit = SubmitField("Register")

    #checks ida user already exists
    def validate_username(self, username):
        existing_user = mongo.db.users.find_one({"username": username.data})
        if existing_user:
            #kima throw mais brk raise te3 Error
            raise ValidationError("That username is already taken, please pick another one.")

#the login form , wch lzm t3mr ki tji ha dir login
class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=8, max=16)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=16)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Login")

#the book form
class BookForm(FlaskForm):
    #attribut te3 el book
    nameBook = StringField(validators=[InputRequired(), Length(min=0 , max=20)], render_kw={"placeholder": "Book Name"})
    #add and delete the book (submit fields)
    add_submit = SubmitField('Add Book')
    delete_submit = SubmitField('Delete Book')

class ManagerUsers(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=8, max=16)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=16)], render_kw={"placeholder": "Password"})
    birthdate = DateField('Birthdate', format='%Y-%m-%d', validators=[InputRequired()], render_kw={"placeholder": "YYYY-MM-DD"})
    name = StringField(validators=[InputRequired(), Length(min=2 , max=20)], render_kw={"placeholder":"Name"})
    role = StringField(validators=[InputRequired(),Length(min=4 , max=10)],render_kw={"placeholder":"Role"})
    add_submit = SubmitField('Add User')
    delete_submit = SubmitField('Delete User')