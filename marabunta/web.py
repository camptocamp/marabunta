# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import os

from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple


class WebApp(object):

    def __init__(self, host, port, custom_maintenance_file=None):
        self.host = host
        self.port = port
        if not custom_maintenance_file:
            custom_maintenance_file = os.path.join(
                os.path.dirname(__file__),
                'html/migration.html'
            )
        with open(custom_maintenance_file, 'r') as f:
            self.maintenance_html = f.read()

    def serve(self):
        run_simple(self.host, self.port, self)

    def dispatch_request(self, request):
        return Response(self.maintenance_html, mimetype='text/html')

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)
