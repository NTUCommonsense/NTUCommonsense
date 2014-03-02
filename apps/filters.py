# -*- coding: utf-8 -*-

from mistune import Markdown


def init_app(app):
    md = Markdown(escape=True)
    app.jinja_env.filters['markdown'] = md.render
