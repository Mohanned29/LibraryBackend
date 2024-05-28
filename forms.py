from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField, FileField
from wtforms.validators import InputRequired, Length, ValidationError


class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=8, max=16)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=16)], render_kw={"placeholder": "Password"})
    birthdate = DateField('Birthdate', format='%Y-%m-%d', validators=[InputRequired()], render_kw={"placeholder": "YYYY-MM-DD"})
    name = StringField(validators=[InputRequired(), Length(min=2, max=20)], render_kw={"placeholder": "Name"})
    submit = SubmitField("Register")

    def validate_username(self, username):
        from app import mongo
        existing_user = mongo.db.users.find_one({"username": username.data})
        if existing_user:
            raise ValidationError("That username is already taken, please pick another one.")

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=8, max=16)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=16)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Login")

class BookForm(FlaskForm):
    nameBook = StringField(validators=[InputRequired(), Length(min=1, max=100)], render_kw={"placeholder": "Book Name"})
    category = StringField(validators=[InputRequired(), Length(min=1, max=50)], render_kw={"placeholder": "Category"})
    add_submit = SubmitField('Add Book')

class ManagerUsers(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=8, max=16)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=16)], render_kw={"placeholder": "Password"})
    birthdate = DateField('Birthdate', format='%Y-%m-%d', validators=[InputRequired()], render_kw={"placeholder": "YYYY-MM-DD"})
    name = StringField(validators=[InputRequired(), Length(min=2, max=20)], render_kw={"placeholder": "Name"})
    role = StringField(validators=[InputRequired(), Length(min=4, max=10)], render_kw={"placeholder": "Role"})
    add_submit = SubmitField('Add User')
    delete_submit = SubmitField('Delete User')