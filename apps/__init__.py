# -*- coding: utf-8 -*-

from flask import Flask

from .models import db

__all__ = ('create_app', 'db')

_MODULES = {
    'projects': '/',
    'admin': '/admin'
}


def create_app(name=None, create_db=False):
    if name is None:
        name = __name__

    app = Flask(name)
    app.config.from_object('config')

    db.app = app
    db.init_app(app)
    if create_db:
        db.create_all()

    for name, url_prefix in _MODULES.iteritems():
        module = 'modules.{}.views'.format(name)
        views = __import__(module, globals(), locals(), ('module',), -1)
        app.register_blueprint(views.module, url_prefix=url_prefix)

    return app
