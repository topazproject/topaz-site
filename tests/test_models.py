import datetime

from topaz_site.models import Build


class TestModels(object):
    def create_build(self, models):
        sha1 = "a" * 40
        platform = "osx"
        success = True
        timestamp = datetime.datetime.utcnow()
        with models.engine.connect() as conn:
            result = conn.execute(models.builds.insert().values(
                sha1=sha1,
                platform=platform,
                success=success,
                timestamp=timestamp
            ))
        [id] = result.inserted_primary_key
        return Build(
            id=id, sha1=sha1, platform=platform, success=success,
            timestamp=timestamp
        )

    def test_get_builds(self, models):
        orig_build = self.create_build(models)
        builds = models.get_builds()
        assert len(builds) == 1
        [build] = builds
        assert build.id == orig_build.id
        assert build.sha1 == orig_build.sha1
        assert build.platform == orig_build.platform
        assert build.success == orig_build.success
        assert build.timestamp == orig_build.timestamp
