# -*- coding: utf-8 -*-

from flask import (Blueprint, request, url_for, redirect, abort, flash,
                   render_template)
from flask.ext.login import (current_user, login_user, logout_user,
                             login_required)
from HTMLMinifier import minify

from .forms import (SigninForm, UserForm, SignupForm, PublicationForm,
                    ApplicationForm, ParameterForm, InterfaceForm,
                    DownloadForm, ProjectForm)
from .models import User, Project, Interface

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


def _create_project_item(Model, item_type, project):
    if item_type == 'param':
        api_id = request.args.get('api_id')
        api = Interface.get(api_id)
        if api is None or api.project_id != project.id:
            return abort(404)

        item = Model(api_id=api_id)
    else:
        item = Model(project_id=project.id)

    return item


def _get_project_item(Model, item_type, project, item_id):
    item = Model.get(id=item_id)
    if item is None:
        return None

    is_valid_item = False
    if item_type == 'param':
        api = Interface.get(item.api_id)
        is_valid_item = api is not None and api.project_id == project.id
    else:
        is_valid_item = item.project_id == project.id

    return item if is_valid_item else None


def _get_page_after_action(item_type, project, item):
    if item_type == 'param':
        target = url_for('.edit_item', project=project.short_name,
                         item_type='api', id=item.api_id)
    else:
        target = url_for('.edit_project', project=project.short_name)

    return target


@module.route('/')
def index():
    return _render_template('index.html')


@module.route('/projects')
@login_required
def show_projects():
    if not current_user.is_admin:
        return abort(403)

    return _render_template('list_projects.html')


@module.route('/project/<project>')
def show_project(project):
    project = Project.query.filter_by(short_name=project).first_or_404()
    sections = [('pubs', 'Publications'),
                ('apps', 'Applications'),
                ('apis', 'Web APIs'),
                ('contact', 'Contact Information')]
    return _render_template('show_project.html',
                            project=project, sections=sections)


@module.route('/project/<project>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(project):
    project = Project.query.filter_by(short_name=project).first_or_404()
    if not current_user.is_admin and current_user not in project.managers:
        return abort(403)

    form = ProjectForm(request.form, obj=project)
    if form.validate_on_submit():
        form.populate_obj(project)
        project.save()

        flash('Project infromation was successfully updated.')
        return redirect(url_for('.edit_project', project=project.short_name))

    subfields = [('pub', 'Publications', 'pubs', {}),
                 ('app', 'Applications', 'apps', {}),
                 ('api', 'Web APIs', 'apis', {}),
                 ('download', 'Downloads', 'downloads', {})]
    return _render_template('edit_item.html', name=Project.__caption__,
                            form=form, project=project, item=project,
                            subfields=subfields)


@module.route('/project/new', methods=['GET', 'POST'])
@login_required
def create_project():
    if not current_user.is_admin:
        return abort(403)

    project = Project()
    form = ProjectForm(request.form, obj=project)
    if form.validate_on_submit():
        form.populate_obj(project)
        project.save()

        flash('Project was successfully created.')
        return redirect(url_for('.edit_project', project=project.short_name))

    return _render_template('edit_item.html', name=Project.__caption__,
                            form=form, project=project, item=project,
                            subfields=[])


@module.route('/project/<project>/edit/<item_type>', methods=['GET', 'POST'])
@login_required
def edit_item(project, item_type):
    project = Project.query.filter_by(short_name=project).first_or_404()
    Form = _FORMS.get(item_type)
    if Form is None:
        return abort(404)

    if not current_user.is_admin and current_user not in project.managers:
        return abort(403)

    Model = Form.Meta.model
    item_id = request.args.get('id')
    if item_id is None:
        item = _create_project_item(Model, item_type, project)
    else:
        item = _get_project_item(Model, item_type, project, item_id)
        if item is None:
            return abort(404)

    form = Form(request.form, obj=item)
    if form.validate_on_submit():
        form.populate_obj(item)
        item.save()

        flash('{0} was successfully updated.'.format(Model.__caption__))
        target = _get_page_after_action(item_type, project, item)
        return redirect(target)

    subfields = []
    if item_id is not None and item_type == 'api':
        subfields = [('param', 'Parameters', 'params', {'api_id': item.id})]

    return _render_template('edit_item.html', name=Model.__caption__,
                            form=form, project=project, item=item,
                            subfields=subfields)


@module.route('/project/<project>/delete/<item_type>')
@login_required
def delete_item(project, item_type):
    project = Project.query.filter_by(short_name=project).first_or_404()
    if not current_user.is_admin and current_user not in project.managers:
        return abort(403)

    item_id = request.args.get('id')
    if item_id is None:
        return abort(404)

    Form = _FORMS.get(item_type)
    Model = Form.Meta.model
    item = _get_project_item(Model, item_type, project, item_id)
    if item is None:
        return abort(404)

    if request.args.get('confirmed'):
        item.delete()

        flash('{0} was successfully deleted.'.format(Model.__caption__))
        target = _get_page_after_action(item_type, project, item)
        return redirect(target)

    return _render_template('delete_item.html', name=Model.__caption__,
                            project=project, item=item)


@module.route('/users')
@login_required
def show_users():
    if not current_user.is_admin:
        return abort(403)

    return _render_template('list_users.html', users=User.query.all())


@module.route('/user/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if not current_user.is_admin and current_user.id != user_id:
        return abort(403)

    user = User.get(user_id)
    if user is None:
        return abort(404)

    form = UserForm(request.form, obj=user)
    if form.validate_on_submit():
        if not current_user.is_admin:
            form.projects.data = user.projects
            form.is_admin.data = user.is_admin
        elif current_user.id == user_id:
            form.is_admin.data = True

        form.populate_obj(user)
        user.save()

        flash('User information was successfully updated.')
        return _render_template('edit_user.html', form=form)

    return _render_template('edit_user.html', form=form)


@module.route('/user/new', methods=['GET', 'POST'])
@login_required
def create_user():
    if not current_user.is_admin:
        return abort(403)

    user = User()
    form = SignupForm(request.form, obj=user)
    if form.validate_on_submit():
        form.populate_obj(user)
        user.save()
        return redirect(url_for('.show_users'))

    return _render_template('edit_user.html', form=form)


@module.route('/signin', methods=['GET', 'POST'])
def signin():
    if current_user is not None and current_user.is_authenticated():
        return redirect(url_for('.index'))

    form = SigninForm(request.form)
    if form.validate_on_submit():
        login_user(form.user, remember=form.remember.data)
        return redirect(request.args.get('next') or url_for('.index'))

    return _render_template('signin.html', form=form)


@module.route('/signout')
@login_required
def signout():
    logout_user()
    return redirect(url_for('.index'))
