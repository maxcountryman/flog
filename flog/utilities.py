from flog import app

from flask import (session, g, flash, request, url_for, redirect, 
        render_template, abort)
from flaskext.bcrypt import check_password_hash

from wtforms.validators import ValidationError

import re
from unicodedata import normalize
from functools import wraps

_punctuation_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')

def slugify(text, delimiter=u'-'):
    result = []
    for word in _punctuation_re.split(text.lower()):
        word = normalize('NFKD', word).encode('ascii', 'ignore')
        if word:
            result.append(word)
    return unicode(delimiter.join(result))

def is_hashed(form, field):
    if not check_password_hash(g.user.pwhash, field.data):
        raise ValidationError('Invalid password')

def auth_user(user):
    g.user = user
    g.username = user.username
    g.pwhash = user.pwhash
    session['logged_in'] = True
    session['username'] = user.username
    flash('You are logged in as {0}'.format(user.username))

def deauth_user():
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('You were logged out')

def whitelist(f):
    '''This decorator function is used to limit access to a view based on a 
    whitelist of IPs which may be configured in the apps config by setting 
    `SITE_WHITELIST` to a list of allowed IPs.
    '''
    
    @wraps(f)
    def inner(*args, **kwargs):
        if not request.remote_addr in app.config.get('SITE_WHITELIST', []):
            return abort(403)
        return f(*args, **kwargs)
    return inner

def login_required(f):
    '''This functuon checks whether we have `logged_in` set to `True`. If not 
    it redirects to the login page.
    '''
    
    @wraps(f)
    def inner(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return inner

def is_superuser(f):
    '''This function checks whether we have `is_staff` set to `True`. If not 
    it redirects to the index page.
    '''
    
    @wraps(f)
    def inner(*args, **kwargs):
        if not session.get('is_staff'):
            error = 'Invalid user permissions' 
            return render_template('index.html', error=error)
        return f(*args, **kwargs)
    return inner

@app.template_filter('formatdate')
def formatdate(value, format='%H:%M / %d-%m-%Y'):
    return value.strftime(format)

def url_for_other_page(page):
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)

app.jinja_env.globals['url_for_other_page'] = url_for_other_page

