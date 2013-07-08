import datetime
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

    def test_redirect_root(self, application):
        c = Client(application, BaseResponse)
        response = c.get("/")
        assert response.status_code == 302
        assert response.headers["Location"] == "http://docs.topazruby.com"

    def test_create_build_bad_secret(self, application):
        c = Client(application, BaseResponse)
        response = c.post("/builds/create/", data={
            "build_secret": application.config["core"]["build_secrets"][0] + "bar",
        })
        assert response.status_code == 403

    def test_create_buid(self, application):
        c = Client(application, BaseResponse)
        response = c.post("/builds/create/", data={
            "build_secret": application.config["core"]["build_secrets"],
            "sha1": "a" * 40,
            "platform": "osx64",
            "success": "true",
            "build": (BytesIO("a build!"), "topaz-osx64-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.tar.bz2"),
        })
        assert response.status_code == 201
        assert application.models.engine.execute(select([func.count(application.models.builds.c.id)])).scalar() == 1
        assert application.storage.get_content("topaz-osx64-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.tar.bz2") == "a build!"

    def test_list_builds(self, application):
        c = Client(application, BaseResponse)
        response = c.get("/builds/")
        assert response.status_code == 200

        application.models.create_build(
            sha1="a" * 40, platform="osx64", success=True,
            timestamp=datetime.datetime.utcnow(), filename="abc"
        )
        response = c.get("/builds/")
        assert response.status_code == 200
        assert "a" * 40 in response.data

    def test_list_platform_builds(self, application):
        application.models.create_build(
            sha1="a" * 40, platform="osx64", success=True,
            timestamp=datetime.datetime.utcnow(), filename="abc"
        )
        application.models.create_build(
            sha1="b" * 40, platform="osx32", success=True,
            timestamp=datetime.datetime.utcnow(), filename="abc"
        )

        c = Client(application, BaseResponse)
        response = c.get("/builds/osx32/")
        assert response.status_code == 200
        assert "a" * 40 not in response.data

    def test_latest(self, application):
        application.models.create_build(
            sha1="a" * 40, platform="osx64", success=True,
            timestamp=datetime.datetime.utcnow(), filename="abc"
        )
        c = Client(application, BaseResponse)
        response = c.get("/builds/osx64/latest/")
        assert response.status_code == 302
        assert response.headers["Location"] == "http://builds.topazruby.com/abc"

        response = c.get("/builds/osx32/latest/")
        assert response.status_code == 404
