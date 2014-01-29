# -*- coding: utf-8 -*-

from flask import request, url_for, redirect, render_template
from flask.ext.login import current_user, login_user, logout_user, login_required

from . import module
from ...forms import SigninForm


@module.route('/')
@login_required
def index():
    return render_template('index.html')


@module.route('/login', methods=['GET', 'POST'])
def login():
    if current_user is not None and current_user.is_authenticated():
        return redirect(url_for('admin.index'))

    form = SigninForm(request.form)
    if form.validate_on_submit():
        login_user(form.user)
        return redirect(request.args.get('next') or url_for('admin.index'))

    return render_template('admin/signin.html', form=form)


@module.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('projects.index'))
