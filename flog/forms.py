from flog.utilities import is_hashed

from wtforms import (Form, TextField, TextAreaField, PasswordField, 
        validators)

optional = [validators.Optional()]
required = [validators.Required()]
username_validators = [validators.Length(min=6, max=28)]
email_validators = [validators.Length(min=6, max=35), validators.Email()]
pass_validators = [
                validators.Required(),
                validators.EqualTo('pass_two', message='Passwords must match.'),
                validators.Length(min=6, max=35),
                ]
title_validators = [validators.Required(), validators.Length(max=140)]


class Registration(Form):
    username = TextField(u'Username', validators=username_validators)
    email = TextField(u'Email Address', email_validators)
    pass_one = PasswordField(u'Password', pass_validators)
    pass_two = PasswordField(u'Confirm Password', required)


class Login(Form):
    username = TextField(u'Username', required)
    password = PasswordField(u'Password', required)


class EditUser(Form):
    email = TextField(u'Email Address', email_validators)
    old_pass = PasswordField(u'Current Password', [validators.Required(), is_hashed])
    pass_one = PasswordField(u'New Password', pass_validators)
    pass_two = PasswordField(u'Confirm Password', required)


class AddPost(Form):
    title = TextField(u'Title', title_validators)
    body = TextAreaField(u'Body', required)
    tags = TextField(u'Tags', optional)


class EditPost(AddPost):
    pass
