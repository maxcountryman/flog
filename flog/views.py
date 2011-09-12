from flog import app, db
from flog.forms import Login, Registration, EditUser, AddPost, EditPost
from flog.models import User, Post, Tag, Category
from flog.utilities import auth_user, deauth_user, login_required, whitelist

from flask import (request, session, url_for, redirect, render_template, 
        abort, flash)

from flaskext.bcrypt import check_password_hash, generate_password_hash
from flaskext.csrf import csrf_exempt

from werkzeug.contrib.atom import AtomFeed

import markdown

from urlparse import urljoin

@app.before_request
def before_request():
    pass

@app.after_request
def after_request(response):
    return response

@app.route('/')
def index():
    '''This is the main view. It will return the rendered template based on 
    index.html.'''
    
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    
    if session.get('logged_in'):
        return redirect(url_for('user', id=session.get('username')))
    
    error = None
    form = Login(request.form)
    if request.method == 'POST' and form.validate():
        user = User.query.filter_by(username=form.username.data).first()
        if not user or not user.is_active:
            error = 'Invalid username'
        elif check_password_hash(user.pwhash, form.password.data):
            auth_user(user)
            return redirect(url_for('index'))
        else:
            error = 'Invalid password'
    return render_template('login.html', form=form, error=error)

@app.route('/logout')
def logout():
    
    deauth_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
@whitelist
def register():
    
    if session.get('logged_in'):
        flash('You\'re already registered')
        return redirect(url_for('user', id=session.get('username')))
    
    error = None
    form = Registration(request.form)
    if request.method == 'POST' and form.validate():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            error = 'User exists already'
        else:
            user = User(
                username = form.username.data.lower(),
                pwhash = generate_password_hash(form.pass_one.data),
                email = form.email.data,
                )
            db.session.add(user)
            db.session.commit()
            auth_user(user)
            flash('You were successfully registered and are logged in')
            return redirect(url_for('index'))
    return render_template('register.html', form=form, error=error)

@whitelist
@login_required
@app.route('/user', methods=['GET', 'POST'])
def user():
    user = request.args['id']
    user = User.query.filter_by(username=user).first_or_404()
    form = EditUser(request.form, obj=user)
    if request.method == 'POST' and form.validate():
        form.populate_obj(user)
        user.pw_hash = generate_password_hash(form.newpass.data)
        user.email = form.email.data
        db.session.add(user)
        db.session.commit()
        flash('Your account was successfully updated')
    return render_template('user.html', user=user, form=form)

@login_required
@app.route('/user', methods=['GET', 'DELETE'])
def delete_user():
    user = request.args['id']
    user = User.query.filter_by(username=user).first_or_404()
    if request.method == 'DELETE' or request.args.get('action') == 'delete':
        if user.username != session['username'] or not user.is_staff:
            return abort(500)
        user = user.is_active = False
        db.session.add(user)
        db.session.commit()
        flash('Account successfully deleted')
        return logout()

@app.route('/posts/', defaults={'page': 1})
@app.route('/posts/<int:page>')
def show_posts(page):
    per_page = app.config.get('POSTS_PER_PAGE', 5) # defaults to five
    posts = Post.query.order_by(Post.pub_date.desc()).paginate(page, per_page)
    if not posts and page != 1:
        abort(404)
    return render_template('posts.html', pagination=posts, page=page)

@app.route('/post/<slug>')
def show_post(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    tags = post.tags
    return render_template('post.html', post=post, tags=tags)

@app.route('/post/new', methods=['GET', 'POST'])
@csrf_exempt
@login_required
def add_post():
    form = AddPost(request.form)
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
        return redirect(url_for('show_post', slug=post.slug))
    return render_template('add_post.html', form=form)

@app.route('/post/edit/<slug>', methods=['GET', 'POST'])
@csrf_exempt
@login_required
def edit_post(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    form = EditPost(request.form, obj=post)
    if request.method == 'POST' and form.validate():
        form.populate_obj(post)
        user = User.query.filter_by(
                    username=session.get('username')
                    ).first_or_404()
        post.author = user.username
        post.title = form.title.data
        post.body = markdown.markdown(form.body.data)
        db.session.add(post)
        db.session.commit()
        if form.tags.data:
            for tag in form.tags.data.split(', '):
                tag = Tag.get_or_create(tag)
                tag.posts.append(post)
                db.session.commit()
        flash('Successfully updated post')
        return redirect(url_for('show_post', slug=post.slug))
    return render_template('add_post.html', form=form)

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

def make_external(url):
    return urljoin(request.url_root, url)

@app.route('/recent.atom')
def recent_feed():
    feed = AtomFeed('Recent Posts',
                    feed_url=request.url, url=request.url_root)
    posts = Post.query.order_by(Post.pub_date.desc()) \
                      .limit(15).all()
    for post in posts:
        feed.add(post.title, unicode(post.body),
                 content_type='html',
                 author=post.author,
                 url=make_external(url_for('show_post', slug=post.slug)),
                 updated=post.pub_date,
                 published=post.pub_date)
    return feed.get_response()


if __name__ == '__main__':
    if app.config.get('EXTERNAL', False):
        app.run(host=app.config.get('EXTERNAL_HOST', '192.168.0.1'))
    else:
        app.run()
