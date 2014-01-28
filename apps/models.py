# -*- coding: utf-8 -*-

from flask.ext.sqlalchemy import SQLAlchemy

__all__ = ('db',)

db = SQLAlchemy()


class _CRUDMixin(object):
    __table_args__ = {'extend_existing': True,
                      'sqlite_autoincrement': True}

    id = db.Column(db.Integer, primary_key=True, nullable=False)

    @classmethod
    def get_by_id(cls, id):
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


class Project(_CRUDMixin, db.Model):
    __tablename__ = 'project'

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


class Publication(_CRUDMixin, db.Model):
    __tablename__ = 'publication'

    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))


class Application(_CRUDMixin, db.Model):
    __tablename__ = 'application'

    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))


class Software(_CRUDMixin, db.Model):
    __tablename__ = 'software'

    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))


class Download(_CRUDMixin, db.Model):
    __tablename__ = 'download'

    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))


class Contact(_CRUDMixin, db.Model):
    __tablename__ = 'contact'

    name = db.Column(db.String(32))
    email = db.Column(db.String(64))

    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
