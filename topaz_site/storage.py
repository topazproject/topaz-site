from boto.s3.connection import S3Connection
from boto.s3.key import Key


class FakeStorage(object):
    def __init__(self, config):
        super(FakeStorage, self).__init__()
        self.config = config
        self.files = {}

    def save(self, filename, data):
        self.files[filename] = data


class S3Storage(object):
    def __init__(self, config):
        super(S3Storage, self).__init__()
        self.aws_access_key_id = config["s3"]["aws_access_key_id"]
        self.aws_secret_access_key = config["s3"]["aws_secret_access_key"]
        self.bucket = config["s3"]["bucket"]

    def save(self, filename, data):
        conn = S3Connection(self.aws_access_key_id, self.aws_secret_access_key)
        bucket = conn.get_bucket("topaz-builds")
        k = Key(bucket)
        k.key = filename
        k.set_contents_from_string(data)
        k.set_acl("public-read")
