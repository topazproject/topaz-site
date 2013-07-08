import errno
import os

from boto.s3.connection import S3Connection
from boto.s3.key import Key


class FakeStorage(object):
    def __init__(self, config):
        super(FakeStorage, self).__init__()
        self.files = {}

    def save(self, filename, data):
        self.files[filename] = data

    def get_content(self, filename):
        return self.files[filename]


class DiskStorage(object):
    def __init__(self, config):
        super(DiskStorage, self).__init__()
        self.location = config["storage"]["location"]

    def save(self, filename, data):
        try:
            os.makedirs(self.location)
        except OSError as e:
            if e.errno != errno.EEXIST or not os.path.isdir(self.location):
                raise
        with open(os.path.join(self.location, filename), "wb") as f:
            f.write(data)

    def get_content(self, filename):
        with open(os.path.join(self.location, filename), "rb") as f:
            return f.read()


class S3Storage(object):
    def __init__(self, config):
        super(S3Storage, self).__init__()
        self.aws_access_key_id = config["s3"]["aws_access_key_id"]
        self.aws_secret_access_key = config["s3"]["aws_secret_access_key"]
        self.bucket = config["s3"]["bucket"]

    def save(self, filename, data):
        conn = S3Connection(self.aws_access_key_id, self.aws_secret_access_key)
        bucket = conn.get_bucket(self.bucket)
        k = Key(bucket)
        k.key = filename
        k.set_contents_from_string(data)
        k.set_acl("public-read")
