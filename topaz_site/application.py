import datetime
import json
import os

from jinja2 import Environment, FileSystemLoader

from werkzeug.exceptions import HTTPException, Forbidden, NotFound
from werkzeug.routing import Map, Rule
from werkzeug.utils import redirect
from werkzeug.wrappers import Request, Response

from topaz_site.models import Models
from topaz_site.utils import multi_constant_time_compare


class Application(object):
    def __init__(self, config, storage_cls):
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
            Rule(r"/builds/<platform>/", endpoint=self.list_builds),
            Rule(r"/builds/<platform>/latest/", endpoint=self.latest_build),
            Rule(r"/freenode.ver", endpoint=self.freenode_verification),
            Rule(r"/<path:page>", endpoint=self.other_page),
            Rule(r"/", endpoint=self.other_page),
        ])
        self.storage = storage_cls(config)
        self.build_secrets = config["core"]["build_secrets"].split(",")

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

    def list_builds(self, request, platform=None):
        builds = self.models.get_builds(platform=platform)
        platforms = self.models.get_platforms()
        return self.render_template("builds_list.html",
            builds=builds,
            platforms=platforms,
            current_platform=platform,
        )

    def latest_build(self, request, platform):
        builds = self.models.get_builds(platform=platform, limit=1)
        if not builds:
            raise NotFound
        [build] = builds
        return redirect("http://builds.topazruby.com/%s" % build.filename)

    def create_build(self, request):
        if not multi_constant_time_compare(request.form["build_secret"], self.build_secrets):
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

    def freenode_verification(self, request):
        return Response(self.config["core"]["freenode_verification"])
