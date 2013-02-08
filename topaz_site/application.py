import os

from jina2 import Environment, FileSystemLoader

from werkzeug.exceptions import HTTPException
from werkzeug.routing import Map, Rule
from werkzeug.wrappers import Request, Response

from topaz_site.models import Models


class Application(object):
    def __init__(self, config):
        super(Application, self).__init__()
        self.models = Models(config)
        self.jinja_env = Environment(
            loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")),
            autoescape=True
        )
        self.url_map = Map([
            Rule(r"/builds/", endpoint=self.list_builds),
            Rule(r"/builds/create/", endpoint=self.create_build),
            Rule(r"/<path:page>", endpoint=self.other_page),
        ])

    def __call__(self, environ, start_response):
        request = Request(environ)
        response = self.handle_request(request)
        return response(environ, start_response)

    def handle_request(self, request):
        adapter = self.url_map.bind_to_environ(request)
        try:
            endpoint, args = adapter.match()
            return endpoint(request, **args)
        except HTTPException as e:
            return e

    def render_template(self, template_name, **context):
        t = self.jinja_env.get_template(template_name)
        return Response(t.render(context), mimetype="text/html")

    def list_builds(self, request):
        builds = self.models.get_builds()
        return self.render_template("builds_list.html", builds=builds)
