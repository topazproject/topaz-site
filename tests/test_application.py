from io import BytesIO

from sqlalchemy.sql import select, func

from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse


class TestApplication(object):
    def test_redirect(self, application):
        c = Client(application, BaseResponse)
        response = c.get("/some-random/url/")
        assert response.status_code == 302
        assert response.headers["Location"] == "http://docs.topazruby.com"

    def test_create_build_bad_secret(self, application):
        c = Client(application, BaseResponse)
        response = c.post("/builds/create/", data={
            "build_secret": application.config["core"]["build_secret"] + "bar",
        })
        assert response.status_code == 403

    def test_create_buid(self, application):
        c = Client(application, BaseResponse)
        response = c.post("/builds/create/", data={
            "build_secret": application.config["core"]["build_secret"],
            "sha1": "a" * 40,
            "platform": "osx64",
            "success": "true",
            "build": (BytesIO("a build!"), "topaz-osx64-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.tar.bz2"),
        })
        assert response.status_code == 201
        assert application.models.engine.execute(select([func.count(application.models.builds.c.id)])).fetchone() == (1,)
        assert application.storage.files["topaz-osx64-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.tar.bz2"] == "a build!"
