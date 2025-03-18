from flask import Flask, redirect, url_for, request, render_template, flash, g
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user

# Creates a flask application
app = Flask(__name__)

# Gives SQLalchemy what database to connect to
app.config["SQLALCHEMY_BINDS"] = {"users_db" : "sqlite:///db.sqlite", 
                                  "posts_db" : "sqlite:///posts.sqlite",
                                  }
app.config["SECRET_KEY"] = "daniel"

# Initializes flask-sqlalchemy extension
db = SQLAlchemy()

login_manager =  LoginManager()
login_manager.init_app(app)

# I think this simply creates the database or at least how the database is structured
# Here I describe all the columns needed and their properties
class User(UserMixin, db.Model):
    __bind_key__ = "users_db" # Connects to users_db

    # All acounts must have this infomration because it describes the specific user.
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, 
                         nullable=False)
    password = db.Column(db.String(250), nullable=False)


# Initialize & Create database within app context
db.init_app(app)
with app.app_context():
     db.create_all(bind_key="users_db")
     db.create_all(bind_key="posts_db")
    
@login_manager.user_loader
def load_user(user_id):
     try:
        return User.query.get(user_id)
     except User.DoesNotExist:
         return None

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Check if the username already exists
        existing_user = User.query.filter_by(username=request.form.get("username")).first()
        if existing_user:
            flash("Username already exists. Please choose a different username.")
            return redirect(url_for("register"))
        
        # Create a new user
        user = User(
            username=request.form.get("username"),
            password=request.form.get("password"),
            )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("login"))
    
    return render_template("sign_up.html")

# Route to the login page
@app.route("/login", methods=["GET", "POST"])
def login():
    # If the method is post, so the user is returning something to the app
    # We find the user by filtering for the username
    if request.method == "POST": 
        user = User.query.filter_by(username=request.form.get("username")).first()
        if user and user.password == request.form.get("password"):
            login_user(user)
            flash("You have successfully logged in.")
            return render_template("test.html")
        else:
            return render_template("login.html")
            flash("Invalid username or password.")
    return render_template("login.html")

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.route("/")
def home():
    # The "/" route will lead to the home page
    # return render_template("home.html")
    return render_template("test.html")
################ REPLACE FOR HOME ######################

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/connect")
def connect():
    return render_template("connect.html")

@app.route("/resources")
def resources():
    return render_template("resources.html")




class Post(db.Model):
    __bind_key__ = "posts_db"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    firstName = db.Column(db.String(250), nullable=False)
    lastName = db.Column(db.String(250), nullable=False)
    username = db.Column(db.String(250), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    donation_class = db.Column(db.String(250), nullable=False)
    donation_description = db.Column(db.String(500), nullable=True)
    email = db.Column(db.String(250), nullable=False)


# When making a post, more information must be added to a users id in the data base
# We need the users location, they're donation type and description.
# So when a user is logged in, they should be able to make a post.
# How do you add more information to a database???
@app.route("/connect", methods=["GET", "POST"])
def post():
    if (request.method == "POST"):
        if (current_user.is_authenticated):
            post = Post(firstName = request.form.get("firstName"),
                        lastName = request.form.get("lastName"),
                        username = current_user.username,
                        email = request.form.get("email"),
                        donation_class = request.form.get("donation_class"),
                        location = request.form.get("area"),
                        donation_description = request.form.get("donation_description"),
                        user_id = current_user.id)
            db.session.add(post)
            db.session.commit()
            return redirect(url_for("home")) 
        else:
            return redirect(url_for("login"))
    return render_template("connect.html")


if __name__ == '__main__':
        app.run()