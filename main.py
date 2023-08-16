from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import CreatePostForm, RegisterForm, LoginForm, CommentForm
from flask_gravatar import Gravatar
from functools import wraps
from sqlalchemy import Table, Column, Integer, ForeignKey, MetaData
import os
from recipe_scraper import scrape_me_baby
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy import create_engine, Column, Integer, String, Text
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)
ckeditor = CKEditor(app)
Bootstrap(app)

##CONNECT TO DB - setup for debug or hosting on hekero
# if os.environ.get('DATABASE_URL') == None: #set url for debugging if not on hekero
#     app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///RecipeDB.db")
#     app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
# else:
#     app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
#     app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///RecipeDB.db")
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# old flask method
db = SQLAlchemy(app)

# new flask method
db = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], echo=True)
Session = sessionmaker(bind=db)
session = Session()

#CONFIGURE REALATIONSHIPS
Base = declarative_base()

##CONFIGURE TABLES

class User(UserMixin, Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(100), unique=True)
    password = Column(String(100))
    name = Column(String(1000))
    # posts = relationship("BlogPost", back_populates="author")
    # comments = relationship("Comment", back_populates="comment_author")

class Recipes(Base):
    __tablename__ = "recipes"
    id = db.Column(db.Integer, primary_key=True)
    canonical_url = db.Column(db.String(1000), unique=True, nullable=False)
    title = db.Column(db.String(250), nullable=False)
    total_time = db.Column(db.String(250), nullable=False)
    author = db.Column(db.String(250), nullable=False)
    host = db.Column(db.String(500), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    ingredients = db.Column(db.String(250), nullable=False)



# new
Base.metadata.create_all(db)

# old
# db.create_all()

# setup login bits
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    # return User.query.get(int(user_id))  # old method
    return session.query(User).get(int(user_id))  # new method


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # if hasattr(current_user, 'id'): # Doesnt work!?
        if not current_user.is_authenticated:
            if current_user.id == 1:
                return f(*args, **kwargs)
            else:
                print('user not admin')
                return abort(403)
        else:
            print('logged user not logged in')
            return abort(403)
    return decorated_function


@app.route('/', methods=['GET', 'POST'])
def search_home():
    if request.form:
        search_val = request.form['search_str']
        return redirect(url_for("recipe_search_page", search_val=search_val))
    else:
        return render_template("Test_Index.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == "POST":
        form = request.form
        # name, email, password
        if form:
            password = generate_password_hash(
                form['password'],
                method='pbkdf2:sha256',
                salt_length=8)
            email = form['email']

            # check for existing user:
            # if User.query.filter_by(email=email).first():  # old
            if session.query(User).filter_by(email=email).first():  # new
                flash('Account with email exists')
                return redirect(url_for("login"))

            new_user = User(
                name=form['name'],
                email=email,
                password=password
            )
            session.add(new_user)
            session.commit()
            login_user(new_user, remember=True)
            return redirect(url_for("search_home"))
    return render_template("Test_Register.html", form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == "POST":
        form = request.form
        # name, email, password
        if form:
            password = form['password']
            email = form['email']

            # user = User.query.filter_by(email=email).first()  # old
            user = session.query(User).filter_by(email=email).first()  # new
            if not user:
                print('incorrect user')
                flash('Incorrect credentials')
                return redirect(url_for('login'))
            else:
                if not check_password_hash(user.password, password):
                    flash('Password incorrect')
                    print('incorrect password')
                    return redirect(url_for('login'))
                else:
                    login_user(user, remember=True)
                    print('logged in')
                    return redirect(url_for("search_home"))

    return render_template("Test_Login.html", form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('search_home'))


@app.route("/recipe_search/<search_val>", methods=['GET', 'POST'])
def recipe_search_page(search_val):
    # call back end to search for recipes
    # search_str = request.form['search_str']
    search_str = search_val
    print(search_str)
    search_results, unscrapped_links = scrape_me_baby(search_str, 6)
    scrapped_jsons = [link.to_json() for link in search_results]
    for recipe in scrapped_jsons:
        try:
            recipe['total_time'] = str(int(float(recipe['total_time'])//1)) + ' mins'
        except:
            recipe['total_time'] = 'N/A'
    print(f'Scraped results: {search_results}')
    print(f'Unscraped results: {unscrapped_links}')
    print(f'Scraped json: {scrapped_jsons}')
    return render_template("Test_Recipes.html", recipes=scrapped_jsons, search=search_str)
    # return search_results

@app.route("/recipe_search/<int:recipe_id>", methods=['GET'])
def recipe_card(recipe_id):
    # call back end to show single recipe
    recipes = 1
    # return render_template("recipe_card.html", recipe=recipe)
    return 'hi'


if __name__ == "__main__":
    # app.run(host='0.0.0.0', port=5000)
    app.run(debug=True)
