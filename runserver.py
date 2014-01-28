#!/usr/bin/env python
# -*- coding: utf-8 -*-

from apps import create_app

app = create_app(create_db=True)
app.run()
