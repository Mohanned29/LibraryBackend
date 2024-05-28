from flask import Flask, render_template, url_for, redirect, flash, session
from flask_pymongo import PyMongo
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
        user = mongo.db.users.find_one({"username": form.username.data})
        if user and bcrypt.check_password_hash(user['password'], form.password.data):
            session['username'] = form.username.data
            if user.get('role') == 'admin':
                return redirect(url_for('AdminDash'))
            else:
                flash('Logged in successfully', 'success')
                return redirect(url_for('library'))
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

    # Debugging print statements
    print("Received request at AdminDash")

    if user_form.add_submit.data and user_form.validate_on_submit():
        print("Processing user form")
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
    
    if book_form.add_submit.data and book_form.validate_on_submit():
        print("Processing book form")
        nameBook = book_form.nameBook.data
        category = book_form.category.data

        existing_book = mongo.db.books.find_one({"nameBook": nameBook})
        if existing_book:
            flash("This book already exists in your library!!", "danger")
        else:
            mongo.db.books.insert_one({"nameBook": nameBook, "category": category})
            flash("The book has been added to the database!", 'success')
        return redirect(url_for('AdminDash'))

    users = mongo.db.users.find()
    books = mongo.db.books.find()

    return render_template("admin.html", users=users, books=books, user_form=user_form, book_form=book_form)


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
        if isinstance(birthdate, datetime.datetime):
            birthdate = birthdate.strftime('%Y-%m-%d')
    else:
        flash('User not found!', 'danger')
        return redirect(url_for('login'))

    return render_template("dashboard.html", name=name, birthdate=birthdate)


@app.route("/library", methods=['GET', 'POST'])
def library():
    book_form = BookForm()
    books = list(mongo.db.books.find())
    return render_template("library.html", books=books, book_form=book_form)

#run
if __name__ == '__main__':
    app.run(debug=True)
