from flask.ext.wtf import Form
from wtforms import (StringField, PasswordField,
                     TextAreaField, BooleanField,
                     IntegerField, SelectField,
                     DateTimeField)
from wtforms.validators import DataRequired, Length, Email, InputRequired


class RegisterForm(Form):
    email = StringField('Email address', validators=[
                        DataRequired('Please provide a valid email address'),
                        Length(min=6, message=(u'Email address too short')),
                        Email(message=(u'Not a valid email address.'))])
    password = PasswordField('Pick a secure password', validators=[
                             DataRequired(),
                             Length(min=6, message=(u'Password too short'))])
    name = StringField('Choose your name', validators=[DataRequired()])
    firstname = StringField('First name')
    lastname = StringField('Last name')
    bio = TextAreaField('Biography')
    gender = BooleanField('Gender')
    agree = BooleanField('I agree to all your terms of service', validators=[
                         DataRequired('You must accept our Terms of Service')])


class LoginForm(Form):
    name = StringField('name', validators=[
                       InputRequired(message="Please provide a user or email"),
                       Length(min=3, message=('Minimum of 3 chars'))])
    password = PasswordField('Password', validators=[
                             InputRequired("Please provide a password"),
                             Length(min=6, message=(u'Password too short'))])
    remember_me = BooleanField('Remember me', default=False)


class TaskForm(Form):
    name = StringField('name')
    probe_type = SelectField('Probe Type', default='PingProbe',
                             choices=[('PingProbe', 'Ping'),
                                      ('TraceProbe', 'Trace')])
    dest_addr = StringField('Destination Address',
                            validators=[DataRequired('Invalid IP')])
    run_at = DateTimeField('Run at')
    run_on_nodes = StringField('Run on nodes (seperate with ,)')
    recurrence_count = IntegerField('How often should this reoccur')
    recurrence_time = IntegerField('Reoccur every x seconds')
