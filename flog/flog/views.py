from flog import app
from flog.forms import *
from flog.models import *
from flog.utilities import auth_user, deauth_user, login_required, is_superuser

from flask import Flask, request, session, url_for, redirect, \
    render_template, abort, g, flash, Response

from flaskext.bcrypt import generate_password_hash

from functools import wraps

import markdown

@app.before_request
def before_request():
    pass

@app.after_request
def after_request(response):
    return response

@app.route('/')
def index():
    '''This is the root view. It will return the rendered template based on 
    index.html.'''
    
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    '''Logs the user in.'''
    
    if session.get('logged_in'):
        return redirect(url_for('user', username=session.get('username')))
    
    error = None
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User.query.filter_by(username=form.username.data).first()
        if not user or not user.is_active:
            error = 'Invalid username'
        else:    
            if check_password_hash(user.pw_hash, form.password.data):
                auth_user(user)
                next_url = request.args.get('next')
                if next_url:
                    return redirect(url_for(next_url))
                else:
                    return redirect(url_for('index'))
            else:
                error = 'Invalid password'
    return render_template('login.html', form=form, error=error)

@app.route('/logout')
@login_required
def logout():
    '''Logs the user out.'''
    
    deauth_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    '''This view is used to register new users. If a user is already logged 
    in, i.e. `logged_in` is True then the user is redirected to their profile 
    page.
    
    A form object is passed back to the template that is then used to process 
    the user registration. Form data is grabbed, added to a new instance of 
    the `User` model and then committed to the database.
    
    Finally the user is authenticated with the utility function `auth_user` 
    and is redirected to the index page.
    '''
    
    if session.get('logged_in'):
        flash('You\'re already registered')
        return redirect(url_for('user', username=session.get('username')))
    
    error = None
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            error = 'User exists already'
        else:
            user = User(
                username = form.username.data.lower(),
                pwhash = generate_password_hash(form.password.data),
                email = form.email.data,
                )
            db.session.add(user)
            db.session.commit()
            auth_user(user)
            flash('You were successfully registered and are logged in')
            return redirect(url_for('index'))
    return render_template('register.html', form=form, error=error)

@app.route('/user/<username>', methods=['GET', 'POST', 'DELETE'])
@login_required
def user(username):
    '''Takes one parameter, `username`, and renders the user template. The 
    template is passed a form object which is then used to process and update 
    the user's settings.
    
    Form data is grabbed and added to the appropriate attributes of the 'User'
    model instance `user`. This instance is then added to the database session 
    and committed.
    
    Requires the session variable `logged_in` to be True.
    '''
    
    user = User.query.filter_by(username=username).first_or_404()
    
    if request.method == 'DELETE' or request.args.get('delete') == 'True':
        if user.username != session['username'] or not user.is_staff:
            return abort(500)
        user = user.is_active = False
        db.session.add(user)
        db.session.commit()
        deauth_user()
        flash('Account successfully deleted')
        return redirect(url_for('index'))
    
    form = EditUserForm(request.form, obj=user)
    if request.method == 'POST' and form.validate():
        form.populate_obj(user)
        user.pw_hash = generate_password_hash(form.newpass.data)
        user.email = form.email.data
        db.session.add(user)
        db.session.commit()
        flash('Your account was successfully updated')
    return render_template('user.html', user=user, form=form)

@app.route('/posts/', defaults={'page': 1})
@app.route('/posts/<int:page>')
def show_posts(page):
    per_page = app.config.get('POSTS_PER_PAGE', 5)
    posts = Post.query.order_by(Post.pub_date.desc()).paginate(page, per_page)
    if not posts and page != 1:
        abort(404)
    return render_template('posts.html', pagination=posts, page=page)

@app.route('/post/<slug>')
def show_post(slug):
    post = Post.query.filter_by(slug=slug).first()
    tags = post.tags
    if not post:
        abort(404)
    return render_template('post.html', post=post, tags=tags)

@app.route('/posts/<int:year>/<int:month>', defaults={'page': 1})
@app.route('/posts/<int:year>/<int:month>/<int:page>')
def show_month(year, month, page):
    per_page = app.config.get('POSTS_PER_PAGE', 5)
    posts = Post.query.filter(db.extract('year', Post.pub_date) == year)
    posts = posts.filter(db.extract('month', Post.pub_date) == month)
    posts = posts.order_by(Post.pub_date.desc()).paginate(page, per_page)
    if not posts and page != 1:
        abort(404)
    return render_template('posts.html', pagination=posts, page=page)

@app.route('/tag/<tag>', defaults={'page': 1})
@app.route('/tag/<tag>/<int:page>/')
def show_tag(tag, page):
    per_page = app.config.get('POSTS_PER_PAGE', 5)
    tag = Tag.query.filter_by(name=tag).first_or_404()
    posts = tag.posts.order_by(Post.pub_date.desc()).paginate(page, per_page)
    if not posts and page != 1:
        abort(404)
    return render_template('posts.html', pagination=posts, page=page)

@app.route('/category/<category>', defaults={'page': 1})
@app.route('/category/<category>/<int:page>/')
def show_category(category, page):
    per_page = app.config.get('POSTS_PER_PAGE', 5)
    category = Category.query.filter_by(name=category).first_or_404()
    posts = category.posts.order_by(Post.pub_date.desc()).paginate(page, per_page)
    if not posts and page != 1:
        abort(404)
    return render_template('posts.html', pagination=posts, page=page)

@app.route('/post', methods=['GET', 'POST', 'DELETE'])
def add_post():
    form = AddPostForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User.query.filter_by(
                    username=session.get('username')
                    ).first_or_404()
        post = Post(
                    user.username,
                    form.title.data,
                    markdown.markdown(form.body.data)
                    )
        db.session.add(post)
        db.session.commit()
        for tag in form.tags.data.split(', '):
            tag = Tag.get_or_create(tag)
            tag.posts.append(post)
            db.session.commit()
        flash('Successfully added post')
    if request.args.get('action', None) == 'delete':
        post_id = request.args.get('id')

    if request.args.get('action', None) == 'add':
        return render_template('add_post.html', form=form)
    if request.args.get('edit', False) == 'True':
        return render_template('add_post.html', form=form)
    return redirect(url_for('show_posts'))

if __name__ == '__main__':
    if app.config.get('EXTERNAL', False):
        app.run(host=app.config.get('EXTERNAL_HOST', '192.168.0.1'))
    else:
        app.run()
