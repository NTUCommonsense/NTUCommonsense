# -*- coding: utf-8 -*-

from datetime import datetime

from flask.ext.login import UserMixin
from flask.ext.sqlalchemy import SQLAlchemy
from passlib.hash import sha256_crypt

__all__ = ('db', 'User', 'Publication', 'Application', 'Parameter',
           'Interface', 'Download', 'Project')

db = SQLAlchemy()

project_managers = db.Table(
    'project_managers',
    db.Column('project_id', db.Integer, db.ForeignKey('project.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')))


class _CRUDMixin(object):

    id = db.Column(db.Integer, primary_key=True, nullable=False)

    @classmethod
    def get(cls, id):
        if isinstance(id, (int, float)) or \
           (isinstance(id, basestring) and id.isdigit()):
            return cls.query.get(int(id))
        return None

    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        return instance.save()

    def update(self, commit=True, **kwargs):
        for attr, value in kwargs.iteritems():
            setattr(self, attr, value)
        return commit and self.save() or self

    def save(self, commit=True):
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit=True):
        db.session.delete(self)
        return commit and db.session.commit()


class User(_CRUDMixin, UserMixin, db.Model):
    __tablename__ = 'user'
    __caption__ = 'User'

    email = db.Column(
        db.String(128), nullable=False, index=True, unique=True,
        info={'label': 'Email'})
    pwd = db.Column(
        db.String(256), nullable=False,
        info={'label': 'Password'})
    name = db.Column(
        db.String(32), nullable=False,
        info={'label': 'Name'})
    is_admin = db.Column(
        db.Boolean, default=False, nullable=False,
        info={'label': 'Admin'})

    @classmethod
    def login(cls, email, pwd):
        user = cls.query.filter_by(email=email).first()
        if user is None or not sha256_crypt.verify(pwd, user.pwd):
            return None

        return user

    def set_pwd(self, pwd):
        self.pwd = sha256_crypt.encrypt(pwd)


class Publication(_CRUDMixin, db.Model):
    __tablename__ = 'publication'
    __caption__ = 'Publication'

    title = db.Column(
        db.String(128), nullable=False,
        info={'label': 'Title'})
    authors = db.Column(
        db.String(128), nullable=False,
        info={'label': 'Authors'})
    publisher = db.Column(
        db.String(128), nullable=False,
        info={'label': 'Publisher'})
    date = db.Column(
        db.Date, nullable=False,
        info={'label': 'Publish Date'})

    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))

    def __str__(self):
        return self.title


class Application(_CRUDMixin, db.Model):
    __tablename__ = 'application'
    __caption__ = 'Application'

    name = db.Column(
        db.String(32), nullable=False,
        info={'label': 'Name'})
    url = db.Column(
        db.String(128), nullable=False,
        info={'label': 'URL'})
    img_url = db.Column(
        db.String(128), nullable=False,
        info={'label': 'Image URL'})
    desc = db.Column(
        db.Text, nullable=False,
        info={'label': 'Description'})

    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))

    def __str__(self):
        return self.name


class Parameter(_CRUDMixin, db.Model):
    __tablename__ = 'parameter'
    __caption__ = 'Parameter'

    name = db.Column(
        db.String(32), nullable=False,
        info={'label': 'Name'})
    desc = db.Column(
        db.Text, nullable=False,
        info={'label': 'Description'})

    api_id = db.Column(db.Integer, db.ForeignKey('interface.id'))

    def __str__(self):
        return self.name


class Interface(_CRUDMixin, db.Model):
    __tablename__ = 'interface'
    __caption__ = 'Web API'

    method = db.Column(
        db.Enum('GET', 'POST', 'PUT', 'DELETE'), nullable=False,
        info={'label': 'Method'})
    format = db.Column(
        db.String(128), nullable=False,
        info={'label': 'Format'})
    desc = db.Column(
        db.Text, nullable=False,
        info={'label': 'Description'})
    returns = db.Column(
        db.Text, nullable=False,
        info={'label': 'Returns'})
    example = db.Column(
        db.Text, nullable=False,
        info={'label': 'Example'})

    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))

    params = db.relationship('Parameter', lazy='dynamic')

    def __str__(self):
        return '[ {0} ] {1}'.format(self.method, self.format)


class Download(_CRUDMixin, db.Model):
    __tablename__ = 'download'
    __caption__ = 'Download'

    url = db.Column(
        db.String(128), nullable=False,
        info={'label': 'URL'})
    name = db.Column(
        db.String(32), nullable=False,
        info={'label': 'Name'})

    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))

    def __str__(self):
        return self.name


class Project(_CRUDMixin, db.Model):
    __tablename__ = 'project'
    __caption__ = 'Project'

    name = db.Column(
        db.String(32), nullable=False,
        info={'label': 'Project Name'})
    short_name = db.Column(
        db.String(16), nullable=False, index=True, unique=True,
        info={'label': 'Short Name'})
    short_desc = db.Column(
        db.String(128), nullable=False,
        info={'label': 'Short Description'})
    desc = db.Column(
        db.Text, nullable=False,
        info={'label': 'Description'})
    api_desc = db.Column(
        db.Text, nullable=False,
        info={'label': 'API Description'})
    github_url = db.Column(
        db.String(128),
        info={'label': 'GitHub URL'})
    update_date = db.Column(
        db.DateTime, nullable=False,
        server_default=db.func.now(),
        onupdate=datetime.now)

    pubs = db.relationship('Publication', lazy='dynamic')
    apps = db.relationship('Application', lazy='dynamic')
    apis = db.relationship('Interface', lazy='dynamic')
    downloads = db.relationship('Download', lazy='dynamic')
    managers = db.relationship('User', secondary=project_managers,
                               backref='projects', lazy='dynamic')
