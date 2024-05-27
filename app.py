from flask import Flask, render_template, url_for, redirect, flash
from flask_pymongo import PyMongo
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
import secrets

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/firstdb'
app.config['SECRET_KEY'] = secrets.token_hex(16)

mongo = PyMongo(app)
bcrypt = Bcrypt(app)


class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=8, max=16)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=16)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Register")

    def validate_username(self, username):
        existing_user = mongo.db.users.find_one({"username": username.data})
        if existing_user:
            raise ValidationError("That username is already taken, please pick another one.")


class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=8, max=16)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=16)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Login")


class BookForm(FlaskForm):
    id = 0
    nameBook = StringField(validators=[InputRequired(), Length(min=0 , max=20)], render_kw={"placeholder": "Book Name"})
    submit = SubmitField('Add Book')


@app.route("/")
def home():
    return render_template('home.html')


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = mongo.db.users.find_one({"username": form.username.data})
        if user and bcrypt.check_password_hash(user['password'], form.password.data):
            if user['role'] == 'admin':
                return redirect(url_for('AdminDash'))
            else:
                flash('Logged in successfully', 'success')
                return redirect(url_for('home'))
        else:
            flash('Login unsuccessful, please check username and password', 'danger')
    return render_template("login.html", form=form)


#create:
@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_pass = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        mongo.db.users.insert_one({"username": form.username.data, "password": hashed_pass})
        flash('your account has been created! You are now able to log in', 'success')
        return redirect(url_for("login"))
    return render_template("register.html", form=form)


#read:
@app.route("/AllUsers" , methods =['GET' ,'POST'])
def AllUsers():
    users = mongo.db.users.find()
    return render_template("all_users.html", users=users)


#admin dash:
@app.route("/admin" , methods=['GET','POST'])
def AdminDash():
    return render_template("admin.html")


#Book dash:
@app.route("/Addbook", methods=['GET', 'POST'])
def BookDash():
    form = BookForm()
    if form.validate_on_submit():
        #get the book name from the book form
        nameBook = form.nameBook.data
        #addidng the book to the data base
        mongo.db.books.insert_one({"nameBook": nameBook})
        flash("The book has been added to the database!", 'success')
        return redirect(url_for('BookDash'))
    return render_template("Addbook.html", form=form)


if __name__ == '__main__':
    app.run(debug=True)
