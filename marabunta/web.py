# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from __future__ import annotations

from pathlib import Path

from werkzeug.serving import run_simple
from werkzeug.wrappers import Request, Response


class WebApp:
    def __init__(
        self,
        host: str,
        port: int,
        custom_maintenance_file: str | Path | None = None,
        resp_status: int = 503,
        resp_retry_after: int = 300,
        healthcheck_path: str | None = None,
    ) -> None:
        self.host = host
        self.port = port
        if not custom_maintenance_file:
            custom_maintenance_file = Path(__file__).parent / "html" / "migration.html"
        self.resp_status = resp_status
        self.resp_retry_after = resp_retry_after
        self.healthcheck_path = healthcheck_path
        self.maintenance_html = Path(custom_maintenance_file).read_text()

    def serve(self) -> None:
        run_simple(self.host, self.port, self)

    def dispatch_request(self, request: Request) -> Response:
        if self.healthcheck_path and request.path == self.healthcheck_path:
            # Return HTTP 200 for healthcheck kind of requests
            # It can be used on some platform to know that the service is
            # running as expected.
            return Response(self.maintenance_html, mimetype="text/html")
        return Response(
            self.maintenance_html,
            status=self.resp_status,
            headers={"Retry-After": str(self.resp_retry_after)},
            mimetype="text/html",
        )

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)
