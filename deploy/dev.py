import os
import sys

from werkzeug.debug import DebuggedApplication
from werkzeug.serving import run_simple
from werkzeug.wsgi import SharedDataMiddleware

from topaz_site.application import Application
from topaz_site.storage import DiskStorage
from topaz_site.config import read_config


def main(argv):
    config = read_config(argv[0])
    app = Application(config, DiskStorage)
    app = DebuggedApplication(app)
    app = SharedDataMiddleware(app, {
        "/static/": os.path.join(
            os.path.dirname(__file__), os.pardir, "static"
        ),
    })
    run_simple("localhost", 4000, app)


if __name__ == "__main__":
    main(sys.argv[1:])
