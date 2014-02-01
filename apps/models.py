# -*- coding: utf-8 -*-

from flask.ext.login import UserMixin
from flask.ext.sqlalchemy import SQLAlchemy
from passlib.hash import sha256_crypt

__all__ = ('db',)

db = SQLAlchemy()

project_managers = db.Table('project_managers',
    db.Column('project_id', db.Integer, db.ForeignKey('project.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')))


class _CRUDMixin(object):
    __table_args__ = {'extend_existing': True,
                      'sqlite_autoincrement': True}

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

    email = db.Column(db.String(64), nullable=False, index=True, unique=True)
    pwd = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(32), nullable=False)

    @classmethod
    def login(cls, name, pwd):
        user = cls.query.filter_by(name=name).first()
        if user is None or not sha256_crypt.verify(pwd, user.pwd):
            return None

        return user

    def set_pwd(self, pwd):
        self.pwd = sha256_crypt.encrypt(pwd)


class Publication(_CRUDMixin, db.Model):
    __tablename__ = 'publication'

    title = db.Column(db.String(64), nullable=False)
    authors = db.Column(db.String(64), nullable=False)
    publisher = db.Column(db.String(64), nullable=False)
    date = db.Column(db.Date, nullable=False)

    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))


class Application(_CRUDMixin, db.Model):
    __tablename__ = 'application'

    name = db.Column(db.String(32), nullable=False)
    url = db.Column(db.String(128), nullable=False)
    img_url = db.Column(db.String(128), nullable=False)
    desc = db.Column(db.String(128), nullable=False)

    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))


class Download(_CRUDMixin, db.Model):
    __tablename__ = 'download'

    url = db.Column(db.String(64), nullable=False)
    name = db.Column(db.String(32), nullable=False)

    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))


class Project(_CRUDMixin, db.Model):
    __tablename__ = 'project'

    short_name = db.Column(db.String(16), nullable=False, index=True, unique=True)
    name = db.Column(db.String(32), nullable=False)
    short_desc = db.Column(db.String(128), nullable=False)
    desc = db.Column(db.Text, nullable=False)
    github_url = db.Column(db.String(128))
    update_date = db.Column(db.DateTime, nullable=False,
                            server_default=db.func.now(),
                            onupdate=db.func.current_timestamp())

    pubs = db.relationship('Publication', lazy='dynamic')
    apps = db.relationship('Application', lazy='dynamic')
    downloads = db.relationship('Download', lazy='dynamic')
    managers = db.relationship('User', secondary=project_managers, lazy='dynamic')
