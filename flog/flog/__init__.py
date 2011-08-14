from flask import Flask

from flaskext.csrf import csrf
from flaskext.bcrypt import bcrypt_init
from flaskext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('flog.config.ConfigDebug')

db = SQLAlchemy(app)
bcrypt_init(app)
csrf(app)

import flog.views
