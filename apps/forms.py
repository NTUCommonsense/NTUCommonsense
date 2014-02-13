# -*- coding: utf-8 -*-

from flask.ext.wtf import Form
from wtforms.fields import TextField, PasswordField, BooleanField
from wtforms.validators import DataRequired, URL
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField
from wtforms_alchemy import model_form_factory

from .models import (db, User, Publication, Application, Parameter, Interface,
                     Download, Project)


def _get_projects():
    return Project.query.all()


class _ModelForm(model_form_factory(Form)):
    get_session = db.create_scoped_session


class SigninForm(Form):
    email = TextField('Email Address', [DataRequired()])
    pwd = PasswordField('Password', [DataRequired()])
    remember = BooleanField('Remember me')

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.user = None

    def validate(self):
        isvalid = super(SigninForm, self).validate()
        if not isvalid:
            return False

        user = User.login(self.email.data, self.pwd.data)
        if user is None:
            self.email.errors.append('Invalid username or password')
            return False

        self.user = user
        return True


class UserForm(_ModelForm):
    class Meta:
        model = User
        exclude = ('pwd',)

    projects = QuerySelectMultipleField('Projects', [DataRequired()],
                                        query_factory=_get_projects,
                                        get_label='name')


class PublicationForm(_ModelForm):
    class Meta:
        model = Publication


class ApplicationForm(_ModelForm):
    class Meta:
        model = Application
        validators = {
            'url': [URL()],
            'img_url': [URL()]
        }


class ParameterForm(_ModelForm):
    class Meta:
        model = Parameter


class InterfaceForm(_ModelForm):
    class Meta:
        model = Interface


class DownloadForm(_ModelForm):
    class Meta:
        model = Download
        validators = {'url': [URL()]}


class ProjectForm(_ModelForm):
    class Meta:
        model = Project
        exclude = ('update_date',)
        validators = {'github_url': [URL()]}
