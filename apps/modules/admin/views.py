# -*- coding: utf-8 -*-

from flask import render_template

from . import module


@module.route('/')
def signin():
    return render_template('admin/signin.html')
