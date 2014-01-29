# -*- coding: utf-8 -*-

from flask import Flask
from flask.ext.login import LoginManager

from . import filters
from .models import db, User

__all__ = ('create_app',)

_MODULES = {
    'projects': '',
    'admin': '/admin'
}


def create_app(name=None, create_db=False):
    if name is None:
        name = __name__

    app = Flask(name)
    app.config.from_object('config')

    filters.init_app(app)

    db.app = app
    db.init_app(app)
    if create_db:
        db.create_all()

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.user_loader(User.get)
    login_manager.login_view = "/admin/login"

    for name, url_prefix in _MODULES.iteritems():
        module = 'modules.{}.views'.format(name)
        views = __import__(module, globals(), locals(), ('module',), -1)
        app.register_blueprint(views.module, url_prefix=url_prefix)

    return app
