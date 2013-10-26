from sqlalchemy import (
    MetaData, Table, Column, Boolean, Integer, String, Unicode, DateTime,
    create_engine
)
from sqlalchemy.sql import select, func


class Models(object):
    def __init__(self, config):
        super(Models, self).__init__()
        self.metadata = MetaData()
        self.builds = Table(
            "builds", self.metadata,
            Column("id", Integer, primary_key=True),
            Column("sha1", String(40)),
            Column("platform", Unicode),
            Column("success", Boolean),
            Column("timestamp", DateTime),
            Column("filename", String),
        )
        self.engine = create_engine(config["database"]["uri"])

    def _build_from_row(self, row):
        return Build(
            id=row[self.builds.c.id],
            sha1=row[self.builds.c.sha1],
            platform=row[self.builds.c.platform],
            success=row[self.builds.c.success],
            timestamp=row[self.builds.c.timestamp],
            filename=row[self.builds.c.filename],
        )

    def create_build(self, sha1, platform, success, timestamp, filename):
        result = self.engine.execute(self.builds.insert().values(
            sha1=sha1,
            platform=platform,
            success=success,
            timestamp=timestamp,
            filename=filename
        ))
        [id] = result.inserted_primary_key
        return Build(
            id=id, sha1=sha1, platform=platform, success=success,
            timestamp=timestamp, filename=filename,
        )

    def get_builds(self, platform=None, limit=None):
        query = self.builds.select().order_by(self.builds.c.timestamp.desc())
        if platform is not None:
            query = query.where(self.builds.c.platform == platform)
        if limit is not None:
            query = query.limit(limit)
        return [
            self._build_from_row(row)
            for row in self.engine.execute(query)
        ]

    def get_platforms(self):
        query = select([
            self.builds.c.platform, func.count(self.builds.c.id)
        ]).group_by(
            self.builds.c.platform
        ).order_by(
            func.count(self.builds.c.id).desc()
        )
        return [
            row[self.builds.c.platform]
            for row in self.engine.execute(query)
        ]


class Build(object):
    def __init__(self, id, sha1, platform, success, timestamp, filename):
        super(Build, self).__init__()
        self.id = id
        self.sha1 = sha1
        self.platform = platform
        self.success = success
        self.timestamp = timestamp
        self.filename = filename

    def __eq__(self, other):
        if not isinstance(other, Build):
            return NotImplemented
        return self.id == other.id

    def to_json(self):
        return {
            "id": self.id,
            "sha1": self.sha1,
            "platform": self.platform,
            "success": self.success,
            "timestamp": self.timestamp.isoformat(),
            "filename": self.filename,
        }
