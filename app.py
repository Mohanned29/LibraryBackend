from collections.abc import Sequence
from typing import Any, Mapping
from flask import Flask, render_template, url_for, redirect, flash, session
from flask_pymongo import PyMongo
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField , DateField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
import secrets , datetime

#initialise the app and the data base and the secret key
app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/seconddb'
app.config['SECRET_KEY'] = secrets.token_hex(16)

mongo = PyMongo(app)
bcrypt = Bcrypt(app)


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

#route to home page
@app.route("/")
def home():
    return render_template('home.html')


#route to login page
@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        #njbdo el user li dkhl el username te3o
        user = mongo.db.users.find_one({"username": form.username.data})
        #ida username w mdps shih alors enter
        if user and bcrypt.check_password_hash(user['password'], form.password.data):
            #ida role == admin alors
            if user.get('role') == 'admin':
                #roh drct lel admin dash
                return redirect(url_for('AdminDash'))
            else:
                flash('Logged in successfully', 'success')
                return redirect(url_for('home'))
        else:
            flash('Login unsuccessful, please check username and password', 'danger')
    return render_template("login.html", form=form)

#route to registre page
@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        #hash the password for more securite
        hashed_pass = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        #date logic (done by gpt)
        birthdate = form.birthdate.data
        birthdate_datetime = datetime.datetime.combine(birthdate, datetime.datetime.min.time())

        #insert the new user in the data base
        mongo.db.users.insert_one({
            "username": form.username.data,
            "password": hashed_pass,
            "name": form.name.data,
            "birthdate": birthdate_datetime,
            "role": "member"
        })
        #once account created , redirect to login
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for("login"))
    return render_template("register.html", form=form)



#route to admin dash
@app.route("/admin", methods=['GET', 'POST'])
def AdminDash():
    return render_template("admin.html")

#site dashboard , not used yet
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if 'username' not in session:
        flash('You are not logged in!', 'danger')
        return redirect(url_for('login'))

    username = session['username']
    user = mongo.db.users.find_one({"username": username})
    
    if user:
        name = user.get('name', 'N/A')
        birthdate = user.get('birthdate', 'N/A')
    else:
        flash('User not found!', 'danger')
        return redirect(url_for('login'))

    return render_template("dashboard.html", name=name, birthdate=birthdate)


#here you can manage the books (add and delete)
@app.route("/manage_books", methods=['GET', 'POST'])
def manage_books():
    form = BookForm()
    if form.validate_on_submit():
        nameBook = form.nameBook.data
        #ida hbina nzido a book (add book):
        if form.add_submit.data:
            #check if already exists
            existingBook = mongo.db.books.find_one({"nameBook": nameBook})
            if existingBook:
                flash("This book already exists in your library!!", "danger")
            else:
                #sinon ida mkcho already , nzidoh:
                mongo.db.books.insert_one({"nameBook": nameBook})
                flash("The book has been added to the database!", 'success')
        #ida user heb yssuprimi ktab:
        elif form.delete_submit.data:
            result = mongo.db.books.delete_one({"nameBook": nameBook})
            if result.deleted_count > 0:
                flash("The book has been deleted", "success")
            else:
                #book not found flash
                flash("Book not found", "danger")
        return redirect(url_for('manage_books'))
    return render_template("manage_books.html", form=form)

#run
if __name__ == '__main__':
    app.run(debug=True)
