from flask import url_for, session, request, render_template, flash, redirect
from app import app, db
from app import hash_string
from .forms import LoginForm, RegisterForm, TaskForm
from .models import User
from flask.ext.login import login_user, logout_user
from flask.ext.login import current_user, login_required
import json
from pymongo import MongoClient
from bson.objectid import ObjectId


# Lets get this stuff loaded here quickly,
# need to do a LOT of cleanup on the whole frontend
# code as I was just a newbie when i wrote this stuff
# now i'm at least an intermediate newbie at python :)
class TaskStorage:
    def __init__(self, db_addr='127.0.0.1', db_port=27017):
        self.session = MongoClient(db_addr, db_port)
        self.db = self.session.task_database
        self.tasks = self.db.task_collection
        self.task_ids = []

    def get_tasks(self):
        """ Prints out all tasks """
        return self.tasks.find()

    def get_task(self, task_id):
        """ Returns a single task """
        return self.tasks.find_one({"_id": ObjectId(task_id)})


@app.route('/tasks/add', methods=['GET', 'POST'])
def add_task():
    """ Add a task to the database """
    if request.method == 'POST':
        form = TaskForm(request.form)
        if form.validate():
            pass

        return render_template('add_task.html',
                               form=form,
                               title="Add Task")
    else:
        return render_template('add_task.html',
                               form=TaskForm(),
                               title="Add Task")


@app.route('/tasks')
def tasks():
    task_storage = TaskStorage()
    result = task_storage.get_tasks()

    tasks = []
    for task in result:
        tasks.append(task)

    return render_template("tasks.html", tasks=tasks)


@app.route('/task/<task_id>')
def task(task_id):
    task_storage = TaskStorage()
    task = task_storage.get_task(task_id)

    return render_template("task.html", task=task)


@app.route('/', methods=['GET', 'POST'])
def home():
    """The route/view for the main page"""

    # Check if the user is logged on already
    if current_user.is_authenticated:
        user = User.query.filter_by(id=session['id']).first()

        # The form either didn't validate or there was no POST request
        return render_template('home.html',
                               title='Home',
                               user=user)
    else:
        # We're not logged on so point us to the logon/registration page
        return render_template('firstvisit.html',
                               loginform=LoginForm(),
                               registerform=RegisterForm())


@app.route('/users')
@login_required
def user_list():
    """The route/view displaying a list of users.
    Requires the admin user to be logged in"""

    if session['role'] == 'ROLE_ADMIN':
        return render_template('user-list.html',
                               users=User.query.all(),
                               title='List of Users')
    else:
        return redirect(url_for('home'))


@app.route('/user_edit_email', methods=['GET', 'POST'])
def user_edit_email():
    """The route/view for editing a users email address"""

    id = request.form["pk"]
    user = User.query.get(id)
    user.email = request.form["value"]
    result = {}
    db.session.commit()
    return json.dumps(result)


@app.route('/about')
def about():
    """The route/view for diplaying the About page template"""

    return render_template('about.html',
                           title='About')


@app.route('/contact')
def contact():
    """The route/view for displaying the contact template"""

    return render_template('contact.html',
                           title='Contact')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """The route/view for registering a new user"""

    title = 'Register account'
    if request.method == 'POST':
        form = RegisterForm(request.form)

        if form.validate():
            user = User()
            form.populate_obj(user)
            user_exist = User.query.filter_by(name=form.name.data).first()
            email_exist = User.query.filter_by(email=form.email.data).first()

            if user_exist:
                form.name.errors.append('name already taken')

            if email_exist:
                form.email.errors.append('Email already use')

            if user_exist or email_exist:
                return render_template('register.html', form=form, title=title)

            else:
                user.password = hash_string(user.password)
                user.active = True
                db.session.add(user)
                db.session.commit()

                return render_template('register-success.html',
                                       user=user,
                                       title='Registration Success!')
        else:
            return render_template('register.html', form=form, title=title)

    return render_template('register.html', form=RegisterForm(), title=title)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """The route/view for logging into the site"""
    if request.method == 'POST':

        # check if user is authenticated
        if current_user is not None and current_user.is_authenticated:
            return redirect(url_for('home'))

        form = LoginForm(request.form)

        if form.validate():
            user = User.query.filter_by(name=form.name.data).first()

            # check if we matched the username with 'name' field in the db
            if user is None:
                user = User.query.filter_by(email=form.name.data).first()

                # check if we matched the username with 'email' field in the db
                if user is None:
                    form.name.errors.append('name not found')
                    return render_template('login.html',
                                           loginpage_form=form,
                                           title="Login")

            # check if the password matches
            if user.password != hash_string(form.password.data):
                form.password.errors.append('Password did not match')
                return render_template('login.html',
                                       loginpage_form=form,
                                       title="Login")

            # check if the login went ok (e.g. user is_active in db, etc)
            if not login_user(user, remember=form.remember_me.data):
                flash('Something happened trying to log you on,',
                      'is the account active?')
                return render_template('login.html',
                                       loginpage_form=form,
                                       title="Login")

            # Set the session object to the logged in user
            session['signed'] = True
            session['username'] = user.name
            session['id'] = user.id
            session['role'] = user.role

            # What was this again? Have to read up on the tutorial
            if session.get('next'):
                next_page = session.get('next')
                session.pop('next')
                return redirect(next_page)

            # user is logged on succesfully, lets return him home
            else:
                return redirect(url_for('home'))

            # do we need this return statement still? Think we covered it?
            return render_template('login.html',
                                   loginpage_form=form,
                                   title="Login")

    session['next'] = request.args.get('next')
    return render_template('login.html',
                           loginpage_form=LoginForm(),
                           title="Login")


@app.route('/logout')
def logout():
    """The route/view for logging out a user"""

    session.pop('signed')
    session.pop('username')
    logout_user()
    return redirect(url_for('home'))


@app.route('/profile')
@login_required
def profile():
    """The route/view for displaying user profile"""

    user = User.query.filter_by(name=session['username']).first()
    return render_template('profile.html',
                           title='Customize your profile',
                           user=user)


@app.route('/terms_of_service')
def terms_of_service():
    """The route/view for displaying the terms of service"""
    return render_template('terms_of_service.html', title='Terms of Service')


@app.errorhandler(404)
def page_not_found_error(error):
    """The route/view for redirecting 404 error
    messages to the 404.html template"""

    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """The route/view for redirecting 404 error
    messages to the 500.html template"""

    # if the error was caused by a SQL issue
    # the following command will rollback any changes
    db.session.rollback()

    return render_template('500.html'), 500
