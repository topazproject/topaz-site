class TestModels(object):
    def test_get_builds(self, models):
        orig_build = self.create_build(models)
        builds = models.get_buidls()
        assert len(builds) == 1
        [build] = builds
        assert build.id == orig_build.id
        assert build.sha1 == orig_build.sha1
        assert build.platform == orig_build.platform
        assert build.success == orig_build.success
        assert build.timestamp == orig_build.timestamp
