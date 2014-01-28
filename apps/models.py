# -*- coding: utf-8 -*-

from flask.ext.sqlalchemy import SQLAlchemy

__all__ = ('db',)

db = SQLAlchemy()


class Project(db.Model):
    __tablename__ = 'project'

    id = db.Column(db.Integer, primary_key=True)
    short_name = db.Column(db.String(8), unique=True)
    name = db.Column(db.String(32))
    short_desc = db.Column(db.String(128))
    desc = db.Column(db.Text)
    update_date = db.Column(db.DateTime, server_default=db.func.now(),
                            onupdate=db.func.current_timestamp())

    pubs = db.relationship('Publication', backref='project', lazy='dynamic')
    apps = db.relationship('Application', backref='project', lazy='dynamic')
    softwares = db.relationship('Software', backref='project', lazy='dynamic')
    downloads = db.relationship('Download', backref='project', lazy='dynamic')


class Publication(db.Model):
    __tablename__ = 'publication'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))


class Application(db.Model):
    __tablename__ = 'application'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))


class Software(db.Model):
    __tablename__ = 'software'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))


class Download(db.Model):
    __tablename__ = 'download'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))


class Contact(db.Model):
    __tablename__ = 'contact'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    email = db.Column(db.String(64))

    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
