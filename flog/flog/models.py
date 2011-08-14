from flog import db
from flog.utilities import slugify

from datetime import datetime


class User(db.Model):
    '''This class defines our `User` model. Instantiating this class requires 
    the parameters `username`, `pwhash`, and `email`. 
    
    Optionally, the boolean values for `is_active` and `is_staff` may be 
    indicated. Otherwise they default to `True` and `False`, respectively.'''
    
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, nullable=False)
    pwhash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(254), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_staff = db.Column(db.Boolean, default=False)
    
    def __init__(self, username, pwhash, email):
        self.username = unicode(username)
        self.pwhash = pwhash
        self.email = unicode(email)
        self.is_active = True
        self.is_staff = False
    
    def __repr__(self):
        return '<User {0!r}>'.format(self.username)


class Category(db.Model):
    '''This class defines our `Category` model. Categories are associated with
    `Post` objects by way of a many to many relationship.
    
    In order to create categories without creating duplicates the utility 
    method, `get_or_create` is provided. It takes on parameter, `category_name`
    and returns the instance of the `Category` object.
    
    New `Category` objects can be created as follows:
    
        category = Category('reptiles')
    
    Once a `Category` object is instantiated it must be added to the database 
    session and then committed:
    
        db.session.add(category)
        db.session.commit(category)
    '''
    
    __tablename__ = 'category'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    
    def __init__(self, name):
        self.name = unicode(name)
    
    @classmethod
    def get_or_create(cls, category_name):
        category = cls.query.filter_by(name=category_name).first()
        
        if not category:
            category = cls(category_name)
            db.session.add(category)
            db.session.commit()
            return category
        return category
    
    def __repr__(self):
        return '<Category {0!r}>'.format(self.name)


class Tag(db.Model):
    '''This class defines our `Tag` model. Tags are associated with `Post` 
    objects by way of a many to many relationship.
    
    In order to create tags without creating duplicates the utility method, 
    `get_or_create` is provided. It takes one parameter, `tag_name` and returns
    the instance of the `Tag` object.
    
    New `Tag` objects can be created as follows:
    
        tag = Tag('python')
    
    Once a `Tag` object is instantiated it must be added to the database session 
    and then committed:
    
        db.session.add(tag)
        db.session.commit(tag)
    '''
    
    __tablename__ = 'tag'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    
    def __init__(self, name):
        self.name = unicode(name)
    
    @classmethod
    def get_or_create(cls, tag_name):
        tag = cls.query.filter_by(name=tag_name).first()
        
        if not tag:
            tag = cls(tag_name)
            db.session.add(tag)
            db.session.commit()
            return tag
        return tag
    
    def __repr__(self):
        return '<Tag {0!r}>'.format(self.name)


# Association tables
post_tags = db.Table('post_tags', db.Model.metadata,
    db.Column('post_id', db.Integer, 
              db.ForeignKey('post.id', ondelete='CASCADE')),
    db.Column('tag_id', db.Integer,
              db.ForeignKey('tag.id', ondelete='CASCADE')))

post_categories = db.Table('post_categories', db.Model.metadata,
    db.Column('post_id', db.Integer, 
              db.ForeignKey('post.id', ondelete='CASCADE')),
    db.Column('category_id', db.Integer,
              db.ForeignKey('category.id', ondelete='CASCADE')))


class Post(db.Model):
    '''This class defines our `Post` model. Posts may be related to `Category`
    and `Tag` objects. These relationships are many to many relationships.
    
    Instantiating a new `Post` objects requires the following parameters: 
    `author`, `title`, and `body`. A new post object might be created as 
    follows:
    
        post = Post('Max', 'Pythons are Awesome!', 'Aren't they the coolest?')
    
    Once a new instance is created it must be added to the database session 
    and then committed:
        
        db.session.add(post)
        db.session.commit()
    '''
    
    __tablename__ = 'post'
    
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(80), nullable=False)
    title = db.Column(db.String(156), nullable=False)
    slug = db.Column(db.String(156), nullable=False, unique=True)
    body = db.Column(db.Text)
    pub_date = db.Column(db.DateTime)
    
    # many to many Post<->Category
    categories = db.relationship(
            'Category', 
            secondary='post_categories',
            backref=db.backref('posts', lazy='dynamic')
            )
    
    # many to many Post<->Tag
    tags = db.relationship(
            'Tag', 
            secondary='post_tags', 
            backref=db.backref('posts', lazy='dynamic')
            )
    
    def __init__(self, author, title, body, pub_date=None):
        self.author = unicode(author)
        self.title = unicode(title)
        self.slug = slugify(self.title)
        
        # make sure slugs are unique, if not append a version to them
        i = 2
        while Post.query.filter_by(slug=self.slug).first():
            version = u'-{0}'.format(i)
            if self.slug[-2:] == version:
                self.slug = self.slug[:-2] + u'-{0}'.format(i+1)
                i += 1
            else:
                self.slug = self.slug + version
        
        self.body = body
        
        if pub_date is None:
            pub_date = datetime.now()
        self.pub_date = pub_date
        
    def get_month(self):
        return self.pub_date.month
    
    def get_year(self):
        return self.pub_date.year
    
    def __repr__(self):
        return '<Post {0!r}>'.format(self.title)

