# -*- coding: utf-8 -*-

from markdown import markdown


def init_app(app):
    app.jinja_env.filters['markdown'] = markdown
