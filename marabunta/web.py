# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import os

from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple


class WebApp(object):

    def __init__(self, host, port, custom_maintenance_file=None,
                 resp_status=503, resp_retry_after=300,
                 healthcheck_path=None):
        self.host = host
        self.port = port
        if not custom_maintenance_file:
            custom_maintenance_file = os.path.join(
                os.path.dirname(__file__),
                'html/migration.html'
            )
        self.resp_status = resp_status
        self.resp_retry_after = resp_retry_after
        self.healthcheck_path = healthcheck_path
        with open(custom_maintenance_file, 'r') as f:
            self.maintenance_html = f.read()

    def serve(self):
        run_simple(self.host, self.port, self)

    def dispatch_request(self, request):
        if self.healthcheck_path and request.path == self.healthcheck_path:
            # Return HTTP 200 for healthcheck kind of requests
            # It can be used on some platform to know that the service is
            # running as expected.
            return Response(self.maintenance_html, mimetype='text/html')
        return Response(
            self.maintenance_html,
            status=self.resp_status,
            headers={'Retry-After': self.resp_retry_after},
            mimetype='text/html'
        )

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)
