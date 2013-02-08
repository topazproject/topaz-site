from sqlalchemy import (MetaData, Table, Column, Boolean, Integer, String,
    Unicode, DateTime, create_engine)


class Models(object):
    def __init__(self, config):
        super(Models, self).__init__()
        self.metadata = MetaData()
        self.builds = Table("builds", self.metadata,
            Column("id", Integer, primary_key=True),
            Column("sha1", String(40)),
            Column("platform", Unicode),
            Column("success", Boolean),
            Column("timestamp", DateTime),
        )
        self.engine = create_engine(config["database"]["uri"])

    def _build_from_row(self, row):
        return Build(
            id=row[self.builds.c.id],
            sha1=row[self.builds.c.sha1],
            platform=row[self.builds.c.platform],
            success=row[self.builds.c.success],
            timestamp=row[self.builds.c.timestamp],
        )

    def get_builds(self):
        with self.engine.connect() as conn:
            query = self.builds.select().order_by(self.builds.c.timestamp.desc())
            return [
                self._build_from_row(row)
                for row in conn.execute(query)
            ]


class Build(object):
    def __init__(self, id, sha1, platform, success, timestamp):
        super(Build, self).__init__()
        self.id = id
        self.sha1 = sha1
        self.platform = platform
        self.success = success
        self.timestamp = timestamp
