from flog.utilities import is_hashed

from flaskext.bcrypt import check_password_hash

from wtforms import Form, TextField, TextAreaField, PasswordField, validators


class RegistrationForm(Form):
    username = TextField('Username', [validators.Length(min=4, max=25)])
    
    email = TextField(
        'Email Address', 
        [validators.Length(min=6, max=254), validators.Email()]
        )
    
    password = PasswordField('Password', [
        validators.Required(),
        validators.EqualTo('confirm', message='Passwords must match'),
        validators.Length(min=8, max=128),
        ])
    
    confirm = PasswordField('Confirm Password')


class LoginForm(Form):
    username = TextField('Username', [validators.Required()])
    password = PasswordField('Password', [validators.Required()])


class EditUserForm(Form):
    email = TextField(
        'Email Address', 
        [validators.Length(min=6, max=254), validators.Email()]
        )
    current = PasswordField(
        'Current Password', 
        [validators.Required(), is_hashed]
        )
    newpass = PasswordField(
        'New Password', [
            validators.Required(),
            validators.Length(min=8, max=128),
            validators.EqualTo('confirm', message='Passwords must match'),
            ]
        )
    confirm = PasswordField(
        u'Confirm Password', 
        [validators.Required(), validators.Length(min=8, max=128)]
        )


class AddPostForm(Form):
    title = TextField(
            u'Title', 
            [validators.Required(), validators.Length(max=50)]
            )
    body = TextAreaField(u'Body', [validators.Required()])
    tags = TextField(u'Tags', [validators.Required()])


class EditPostForm(AddPostForm):
    pass
