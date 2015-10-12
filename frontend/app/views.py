from flask import url_for, session, request, render_template, flash, redirect
from app import app, db
from app import hash_string
from .forms import LoginForm, RegisterForm, ProbeForm
from .models import User
from flask.ext.login import login_user, logout_user
from flask.ext.login import current_user, login_required
import json
from pymongo import MongoClient
from bson.objectid import ObjectId
from nvd3 import lineChart
from datetime import datetime
import time


# Lets get this stuff loaded here quickly,
# need to do a LOT of cleanup on the whole frontend
# code as I was just a newbie when i wrote this stuff
# now i'm at least an intermediate newbie at python :)
# also need to merge the Probe and NodeStorage classes
# so we don't have to setup two DB connections

class ProbeStorage:
    def __init__(self, db_addr='127.0.0.1', db_port=27017):
        self.session = MongoClient(db_addr, db_port)
        self.db = self.session.probe_database
        self.probes = self.db.probe_collection
        self.probe_ids = []

    def add(self, probe):
        """ Adds a probe Probe to the database

        Args:
            probe: A dict representing a probe object
        return:
            probe_id: _id value of mongodb document
        """
        return self.probes.insert_one(probe).inserted_id

    def get_probes(self):
        """ Prints out all probes """
        return self.probes.find()

    def get_probe(self, probe_id):
        """ Returns a single probe """
        return self.probes.find_one({"_id": ObjectId(probe_id)})


class NodeStorage:
    def __init__(self, db_addr='127.0.0.1', db_port=27017):
        self.session = MongoClient(db_addr, db_port)
        self.db = self.session.node_database
        self.nodes = self.db.node_collection
        self.node_ids = []

    def clear_db(self):
        """ clears out all db entries """
        self.session.drop_database('node_database')

    def get_nodes(self):
        """ return out all nodes """
        return self.nodes.find()

    def get_node_by_id(self, node_id):
        """ Returns a single node by ID """
        return self.nodes.find_one({"_id": ObjectId(node_id)})

    def delete_node_by_id(self, node_id):
        """ Removes a single node from the db by ID

        TODO: the remove function returns a WriteResult object.
        Need to build in a check to see if it was removed
        succesfully or not
        """
        self.nodes.remove({"_id": ObjectId(node_id)})

    def delete_node_by_name(self, node_name):
        """ Removes a single node from the db by ID

        TODO: the remove function returns a WriteResult object.
        Need to build in a check to see if it was removed
        succesfully or not
        """
        self.nodes.remove({"name": node_name})


# Use a global variable for Probe/NodeStorage, otherwise we need
# to setup a new connection to mongodb for each function

probe_storage = ProbeStorage()
node_storage = NodeStorage()


@app.route('/probes/add', methods=['GET', 'POST'])
def add_probe():
    """ Add a probe to the database

    PingProbe can have the following values:
                'type'
                'recurrence_time'
                'recurrence_count'
                'run_at'
                'dest_addr'
                'timeout'
                'count'
                'preload'

    TraceProbe can have the following values:
                'type'
                'recurrence_time'
                'recurrence_count'
                'run_at'
                'dest_addr'
                'wait_time'
                'max_hops'
    """
    if request.method == 'POST':
        form = ProbeForm(request.form)
        if form.validate():
            probe = {'run_at': time.time(),
                    'type': form.data['probe_type'],
                    'recurrence_time': form.recurrence_time.data,
                    'recurrence_count': form.recurrence_count.data,
                    # 'run_at': form.run_at.data,
                    'dest_addr': form.dest_addr.data,
                    'run_on_nodes': form.run_on_nodes.data.split(',')}
            if form.probe_type == 'PingProbe':
                probe['timeout'] = 1
                probe['count'] = 10
                probe['preload'] = 10
            elif form.probe_type == 'TraceProbe':
                probe['wait_time'] = 1
                probe['max_hops'] = 20

            probe['_id'] = probe_storage.add(probe)
            return render_template('probe_added.html',
                                   form=form,
                                   title="Probe added",
                                   probe=probe)
        return render_template('add_probe.html',
                               form=form,
                               title='Probe added')
    else:
        return render_template('add_probe.html',
                               form=ProbeForm(),
                               title="Add Probe")


@app.route('/probes')
def probes():
    result = probe_storage.get_probes()

    probes = []
    for probe in result:
        probes.append(probe)

    return render_template("probes.html", probes=probes)


@app.route('/probe/<probe_id>')
def probe(probe_id):
    probe = probe_storage.get_probe(probe_id)

    chart = None

    if(probe['type'] == "PingProbe" and
       'result' in probe):
        chart = lineChart(name="lineChart",
                          x_is_date=True,
                          x_axis_format="%d-%m-%y %H:%M:%S",
                          height=250)
        xdata = []
        min_data = []
        avg_data = []
        max_data = []
        for result in probe['result']:
            if 'error' in result:
                # TODO, need to take into account that some probes
                # give an error and some don't This just assumes
                # all probes have errors
                break
            # TODO, Convert timestamp to format using function
            xdata.append(int(result['timestamp'])*1000)
            min_data.append(result['min'])
            avg_data.append(result['avg'])
            max_data.append(result['max'])

        extra_serie = {"tooltip": {"y_start": "There are ", "y_end": " calls"}}
        chart.add_serie(y=min_data, x=xdata, name='min rtt(ms)',
                        extra=extra_serie)
        extra_serie = {"tooltip": {"y_start": "", "y_end": " min"}}
        chart.add_serie(y=avg_data, x=xdata, name='avg rtt(ms)',
                        extra=extra_serie)
        extra_serie = {"tooltip": {"y_start": "", "y_end": " min"}}
        chart.add_serie(y=max_data, x=xdata, name='max rtt(ms)',
                        extra=extra_serie)
        chart.buildcontent()
        chart = chart.htmlcontent

        # convert timestamps for pretty printing
        for item in probe['result']:
            item['timestamp'] = format(datetime.fromtimestamp(item['timestamp']),
                                       '%d-%b-%y - %H:%M:%S')

    return render_template("probe.html", probe=probe, chart=chart)


@app.route('/', methods=['GET', 'POST'])
def home():
    """The route/view for the main page"""

    # Check if the user is logged on already
    if current_user.is_authenticated:
        nodes = node_storage.get_nodes()

        if request.method == 'POST':
            if request.form['delete']:
                # Request.form['delete'] will carry the node_name
                node_storage.delete_node_by_name(request.form['delete'])

        return render_template('home.html',
                               title='Home',
                               nodes=nodes,
                               form=request.form)
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
