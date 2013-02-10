import datetime

from topaz_site.models import Build


class TestModels(object):
    def test_create_build(self, models):
        build = models.create_build(
            sha1="a" * 40, platform="osx64", success=True,
            timestamp=datetime.datetime.utcnow(),
            filename="abc",
        )
        assert build.id is not None
        [result] = models.engine.execute(models.builds.select())
        assert result[models.builds.c.id] == build.id

    def test_get_builds(self, models):
        timestamp = datetime.datetime.utcnow()
        orig_build = models.create_build(
            sha1="a" * 40, platform="osx64", success=True, timestamp=timestamp,
            filename="abc"
        )
        builds = models.get_builds()
        assert len(builds) == 1
        [build] = builds
        assert build.id == orig_build.id
        assert build.sha1 == "a" * 40
        assert build.platform == "osx64"
        assert build.success == True
        assert build.timestamp == timestamp
        assert build.filename == "abc"

    def test_get_platforms(self, models):
        timestamp = datetime.datetime.utcnow()
        models.create_build(
            sha1="a" * 40, platform="osx64", success=True, timestamp=timestamp,
            filename="abc"
        )
        models.create_build(
            sha1="a" * 40, platform="osx64", success=True, timestamp=timestamp,
            filename="abc"
        )
        models.create_build(
            sha1="a" * 40, platform="osx32", success=True, timestamp=timestamp,
            filename="abc"
        )

        assert models.get_platforms() == ["osx64", "osx32"]

    def test_get_builds_for_platform(self, models):
        timestamp = datetime.datetime.utcnow()
        osx64 = models.create_build(
            sha1="a" * 40, platform="osx64", success=True, timestamp=timestamp,
            filename="abc"
        )
        osx32 = models.create_build(
            sha1="a" * 40, platform="osx32", success=True, timestamp=timestamp,
            filename="abc"
        )

        assert models.get_builds(platform="osx32") == [osx32]
        assert models.get_builds() == [osx64, osx32]
