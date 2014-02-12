# -*- coding: utf-8 -*-

from flask import Blueprint, request, url_for, redirect, abort, render_template
from flask.ext.login import current_user, login_user, logout_user, login_required

from .forms import (SigninForm, PublicationForm, ApplicationForm,
                    ParameterForm, InterfaceForm, DownloadForm, ProjectForm)
from .models import Project

module = Blueprint('projects', __name__)

_FORMS = {
    'pub': PublicationForm,
    'app': ApplicationForm,
    'api': InterfaceForm,
    'param': ParameterForm,
    'download': DownloadForm
}


@module.route('/')
def index():
    return render_template('index.html')


@module.route('/project/<project>')
def show_project(project):
    project = Project.query.filter_by(short_name=project).first()
    if project is None:
        return abort(404)

    sections = [('pubs', 'Publications'),
                ('apps', 'Applications'),
                ('apis', 'Web APIs'),
                ('contact', 'Contact Information')]
    return render_template('show_project.html', project=project, sections=sections)


@module.route('/project/<project>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(project):
    project = Project.query.filter_by(short_name=project).first()
    if project is None:
        return abort(404)

    form = ProjectForm(request.form, obj=project)
    if form.validate_on_submit():
        form.populate_obj(project)
        project.save()
        return redirect(url_for('.edit_project', project=project.short_name))

    return render_template('edit_project.html', form=form, project=project)


@module.route('/project/<project>/edit/<type>', methods=['GET', 'POST'])
@login_required
def edit_item(project, type):
    project = Project.query.filter_by(short_name=project).first()
    Form = _FORMS.get(type)
    if project is None or Form is None:
        return abort(404)

    item_id = request.args.get('id')
    Model = Form.Meta.model
    item = Model.query.filter_by(project_id=project.id, id=item_id).first()
    if item is None:
        return abort(404)

    form = Form(request.form, obj=item)
    if form.validate_on_submit():
        form.populate_obj(item)
        item.save()
        return redirect(url_for('.edit_project', project=project.short_name))

    return render_template('edit_item.html', form=form, item=item)


@module.route('/login', methods=['GET', 'POST'])
def login():
    if current_user is not None and current_user.is_authenticated():
        return redirect(url_for('.index'))

    form = SigninForm(request.form)
    if form.validate_on_submit():
        login_user(form.user, remember=form.remember.data)
        return redirect(request.args.get('next') or url_for('.index'))

    return render_template('signin.html', form=form)


@module.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('.index'))
