import os

from raven import Client
from raven.middleware import Sentry

from werkzeug.wsgi import SharedDataMiddleware

from topaz_site.application import Application
from topaz_site.storage import S3Storage


def build_application():
    config = {
        "core": {
            "build_secrets": os.environ["BUILD_SECRETS"],
            "freenode_verification": os.environ["FREENODE_VERIFICATION"],
        },
        "s3": {
            "aws_access_key_id": os.environ["AWS_ACCESS_KEY_ID"],
            "aws_secret_access_key": os.environ["AWS_SECRET_ACCESS_KEY"],
            "bucket": "topaz-builds",
        },
        "database": {
            "uri": os.environ["DATABASE_URL"],
        },
    }
    app = Application(config, S3Storage)
    app = SharedDataMiddleware(app, {
        "/static/": os.path.join(
            os.path.dirname(__file__), os.pardir, "static"
        ),
    })
    return Sentry(
        app,
        Client(os.environ["SENTRY_DSN"])
    )

app = build_application()
