from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse


class TestApplication(object):
    def test_redirect(self, application):
        c = Client(application, BaseResponse)
        response = c.get("/some-random/url/")
        assert response.status_code == 302
        assert response.headers["Location"] == "http://docs.topazruby.com"
