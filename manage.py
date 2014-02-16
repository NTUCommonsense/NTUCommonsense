#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask.ext.script import Manager, prompt, prompt_bool, prompt_pass

from apps import create_app
from apps.models import db, User

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
    name = prompt('Username')
    pwd = prompt_pass('Password')

    user = User(name=name)
    user.set_pwd(pwd)
    user.save()


if __name__ == '__main__':
    manager.run()
