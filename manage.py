#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

from flask.ext.script import Manager, prompt, prompt_bool, prompt_pass
from werkzeug.datastructures import MultiDict

from apps import create_app
from apps.models import db, User
from apps.forms import SignupForm

manager = Manager(create_app)


@manager.command
def initdb():
    '''Creates all database tables.'''
    db.create_all()


@manager.command
def dropdb():
    '''Drops all database tables.'''
    if prompt_bool('Are you sure to drop your databse?'):
        db.drop_all()


@manager.command
def createuser():
    '''Creates a new user for the website.'''
    email = prompt('E-mail')
    name = prompt('Full Name')
    is_admin = prompt_bool('Admin')
    raw_pwd = prompt_pass('Password')
    confirm_pwd = prompt_pass('Confirm Password')

    user = User()
    data = MultiDict(dict(email=email, name=name, is_admin=is_admin,
                          raw_pwd=raw_pwd, confirm_pwd=confirm_pwd))
    form = SignupForm(data, obj=user, csrf_enabled=False)
    if form.validate():
        form.populate_obj(user)
        user.save()

        print('User was successfully created.')
    else:
        for field, errors in form.errors.iteritems():
            field_text = getattr(form, field).label.text
            for error in errors:
                print('[Error] {0}: {1}'.format(field_text, error))


if __name__ == '__main__':
    manager.run()
