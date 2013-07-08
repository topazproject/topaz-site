import pytest


def pytest_addoption(parser):
    group = parser.getgroup("topaz_site tests")
    group.addoption(
        "--config",
        dest="config",
        help="A .ini file with config",
    )


def delete_all_rows(models):
    for table in models.metadata.sorted_tables:
        models.engine.execute(table.delete())


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
    request.addfinalizer(lambda: delete_all_rows(models))
    return models


@pytest.fixture(params=range(2))
def _storage_cls(request):
    from topaz_site.storage import FakeStorage, DiskStorage
    return [FakeStorage, DiskStorage][request.param]


@pytest.fixture
def application(request, _models_setup, _storage_cls):
    from topaz_site.application import Application
    from topaz_site.config import read_config

    config = request.config.getvalueorskip("config")
    application = Application(read_config(config), _storage_cls)
    request.addfinalizer(lambda: delete_all_rows(application.models))
    return application
