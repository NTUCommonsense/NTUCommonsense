# -*- coding: utf-8 -*-

from flask import Blueprint, request, url_for, redirect, abort, render_template
from flask.ext.login import current_user, login_user, logout_user, login_required
from HTMLMinifier import minify

from .forms import (SigninForm, PublicationForm, ApplicationForm,
                    ParameterForm, InterfaceForm, DownloadForm, ProjectForm)
from .models import Project, Interface

module = Blueprint('projects', __name__)

_FORMS = {
    'pub': PublicationForm,
    'app': ApplicationForm,
    'api': InterfaceForm,
    'param': ParameterForm,
    'download': DownloadForm
}


def _render_template(*args, **kwargs):
    html = render_template(*args, **kwargs)
    return minify(html)


@module.route('/')
def index():
    return _render_template('index.html')


@module.route('/project/<project>')
def show_project(project):
    project = Project.query.filter_by(short_name=project).first()
    if project is None:
        return abort(404)

    sections = [('pubs', 'Publications'),
                ('apps', 'Applications'),
                ('apis', 'Web APIs'),
                ('contact', 'Contact Information')]
    return _render_template('show_project.html', project=project, sections=sections)


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

    return _render_template('edit_project.html', form=form, project=project)


@module.route('/project/<project>/edit/<type>', methods=['GET', 'POST'])
@login_required
def edit_item(project, type):
    project = Project.query.filter_by(short_name=project).first()
    Form = _FORMS.get(type)
    if project is None or Form is None:
        return abort(404)

    Model = Form.Meta.model
    item_id = request.args.get('id')
    if item_id is None:
        if type == 'param':
            api_id = request.args.get('api_id')
            api = Interface.get(api_id)
            if api is None or api.project_id != project.id:
                return abort(404)

            item = Model(api_id=api_id)
        else:
            item = Model(project_id=project.id)
    else:
        item = Model.get(id=item_id)
        if item is None:
            return abort(404)

        is_valid_item = False
        if type == 'param':
            api = Interface.get(item.api_id)
            is_valid_item = api is not None and api.project_id == project.id
        else:
            is_valid_item = item.project_id == project.id

        if not is_valid_item:
            return abort(404)

    form = Form(request.form, obj=item)
    if form.validate_on_submit():
        form.populate_obj(item)
        item.save()
        if type == 'param':
            target = url_for('.edit_item', project=project.short_name,
                             type='api', id=item.api_id)
        else:
            target = url_for('.edit_project', project=project.short_name)

        return redirect(target)

    if type == 'api':
        return _render_template('edit_apis.html',
                                form=form, project=project, item=item)

    return _render_template('edit_item.html', name=Model.__name__,
                            form=form, project=project, item=item)


@module.route('/login', methods=['GET', 'POST'])
def login():
    if current_user is not None and current_user.is_authenticated():
        return redirect(url_for('.index'))

    form = SigninForm(request.form)
    if form.validate_on_submit():
        login_user(form.user, remember=form.remember.data)
        return redirect(request.args.get('next') or url_for('.index'))

    return _render_template('signin.html', form=form)


@module.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('.index'))
