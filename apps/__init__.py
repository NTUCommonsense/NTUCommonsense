# -*- coding: utf-8 -*-

from flask import Flask
from flask.ext.login import LoginManager

from . import filters
from .models import db, User, Project
from .views import module

__all__ = ('create_app',)


def _get_projects():
    return Project.query.with_entities(Project.short_name, Project.name).all()


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

    app.jinja_env.globals['get_projects'] = _get_projects

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.user_loader(User.get)
    login_manager.login_view = "/login"

    app.register_blueprint(module)
    return app
