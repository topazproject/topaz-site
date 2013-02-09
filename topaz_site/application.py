import datetime
import json
import os

from jinja2 import Environment, FileSystemLoader

from werkzeug.exceptions import HTTPException, Forbidden
from werkzeug.routing import Map, Rule
from werkzeug.security import safe_str_cmp
from werkzeug.utils import redirect
from werkzeug.wrappers import Request, Response

from topaz_site.models import Models
from topaz_site.storage import FakeStorage, S3Storage


class Application(object):
    def __init__(self, config):
        super(Application, self).__init__()
        self.config = config
        self.models = Models(config)
        self.jinja_env = Environment(
            loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), os.pardir, "templates")),
            autoescape=True
        )
        self.url_map = Map([
            Rule(r"/builds/", endpoint=self.list_builds),
            Rule(r"/builds/create/", endpoint=self.create_build, methods=["POST"]),
            Rule(r"/<path:page>", endpoint=self.other_page),
            Rule(r"/", endpoint=self.other_page),
        ])
        if "s3" in config:
            self.storage = S3Storage(config)
        else:
            self.storage = FakeStorage(config)

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

    def json_response(self, obj, **kwargs):
        kwargs["content_type"] = "application/json"
        return Response(json.dumps(obj.to_json()), **kwargs)

    def list_builds(self, request):
        builds = self.models.get_builds()
        return self.render_template("builds_list.html", builds=builds)

    def create_build(self, request):
        if not safe_str_cmp(request.form["build_secret"], self.config["core"]["build_secret"]):
            raise Forbidden
        self.storage.save(request.files["build"].filename, request.files["build"].read())
        build = self.models.create_build(
            sha1=request.form["sha1"],
            platform=request.form["platform"],
            success=request.form["success"] == "true",
            timestamp=datetime.datetime.utcnow(),
            filename=request.files["build"].filename,
        )
        return self.json_response(build, status=201)

    def other_page(self, request, page=None):
        return redirect("http://docs.topazruby.com")
