import pytest


def pytest_addoption(parser):
    group = parser.getgroup("topaz_site tests")
    group.addoption(
        "--config",
        dest="config",
        help="A .ini file with config",
    )


@pytest.fixture(scope="session")
def _models_setup(request):
    from topaz_site.config import read_config
    from topaz_site.models import Models

    config = request.config.getvalueorskip("config")
    models = Models(read_config(config))
    models.metadata.create_all(models.engine)
    request.addfinalizer(lambda: models.metadata.drop_all(models.engine))


@pytest.fixture
def models(request, _models_setup):
    from topaz_site.config import read_config
    from topaz_site.models import Models

    config = request.config.getvalueorskip("config")
    models = Models(read_config(config))

    def delete_data():
        with models.engine.connect() as conn:
            conn.execute(models.builds.delete())
    request.addfinalizer(delete_data)
    return models


@pytest.fixture
def application(request, _models_setup):
    from topaz_site.application import Application
    from topaz_site.config import read_config

    config = request.config.getvalueorskip("config")
    application = Application(read_config(config))

    def delete_data():
        with application.models.engine.connect() as conn:
            conn.execute(application.models.builds.delete())
    request.addfinalizer(delete_data)
    return application
