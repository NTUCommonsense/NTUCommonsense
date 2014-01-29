# -*- coding: utf-8 -*-

from flask import render_template, abort

from . import module
from ... import models


@module.route('/')
def index():
    return render_template('index.html')


@module.route('/<project>')
def show_project(project):
    project = models.Project.query.filter_by(short_name=project).first()
    if project is None:
        return abort(404)

    return render_template('show_project.html', project=project)
