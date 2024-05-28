from flask import Flask, render_template, url_for, redirect, flash, session
from flask_pymongo import PyMongo
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField , DateField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
import secrets , datetime
from forms import RegisterForm,LoginForm,ManagerUsers,BookForm

#initialise the app and the data base and the secret key
app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/seconddb'
app.config['SECRET_KEY'] = secrets.token_hex(16)

mongo = PyMongo(app)
bcrypt = Bcrypt(app)


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
    user_form = ManagerUsers()
    book_form = BookForm()

    if user_form.add_submit.data and user_form.validate_on_submit():

        username = user_form.username.data
        name = user_form.name.data
        hashed_pass = bcrypt.generate_password_hash(user_form.password.data).decode('utf-8')
        birthdate = user_form.birthdate.data
        birthdate_datetime = datetime.datetime.combine(birthdate, datetime.datetime.min.time())
        role = user_form.role.data

        existing_user = mongo.db.users.find_one({"username": username})
        if existing_user:
            flash("This user already exists", "danger")
        else:
            mongo.db.users.insert_one({"username": username, "name": name, "password": hashed_pass, "birthdate": birthdate_datetime, "role": role})
            flash("User added successfully", "success")
        return redirect(url_for('AdminDash'))
    
    if user_form.delete_submit.data and user_form.username.validate(user_form):

        username = user_form.username.data
        existing_user = mongo.db.users.find_one({"username": username})
        if not existing_user:
            flash("This user doesn't exist", 'danger')
        else:
            mongo.db.users.delete_one({"username": username})
            flash("User deleted successfully", "success")
        return redirect(url_for('AdminDash'))

    if book_form.validate_on_submit():

        nameBook = book_form.nameBook.data
        if book_form.add_submit.data:
            existingBook = mongo.db.books.find_one({"nameBook": nameBook})
            if existingBook:
                flash("This book already exists in your library!!", "danger")
            else:
                mongo.db.books.insert_one({"nameBook": nameBook})
                flash("The book has been added to the database!", 'success')
        
        if book_form.delete_submit.data:
            result = mongo.db.books.delete_one({"nameBook": nameBook})
            if result.deleted_count > 0:
                flash("The book has been deleted", "success")
            else:
                flash("Book not found", "danger")
        return redirect(url_for('AdminDash'))

    users = mongo.db.users.find()
    books = mongo.db.books.find()

    return render_template("admin.html", users=users, books=books, user_form=user_form, book_form=book_form)


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


#run
if __name__ == '__main__':
    app.run(debug=True)
