##################################################################
# Copyright 2019 Open Source Geospatial Foundation and others    #
# licensed under MIT, Please consult LICENSE.txt for details     #
##################################################################

import pywps.configuration as wpsConfig
from . import StorageAbstract
from .implementationbuilder import StorageImplementationBuilder
from . import STORE_TYPE

import os
import logging

LOGGER = logging.getLogger('PYWPS')


class S3StorageBuilder(StorageImplementationBuilder):

    def build(self):
        bucket = wpsConfig.get_config_value('s3', 'bucket')
        prefix = wpsConfig.get_config_value('s3', 'prefix')
        public_access = wpsConfig.get_config_value('s3', 'public')
        encrypt = wpsConfig.get_config_value('s3', 'encrypt')
        region = wpsConfig.get_config_value('s3', 'region')

        return S3Storage(bucket, prefix, public_access, encrypt, region)


def _build_s3_file_path(prefix, filename):
    if prefix:
        path = prefix.rstrip('/') + '/' + filename.lstrip('/')
    else:
        path = filename.lstrip('/')
    return path


def _build_extra_args(public=False, encrypt=False, mime_type=''):
    extraArgs = dict()

    if public:
        extraArgs['ACL'] = 'public-read'
    if encrypt:
        extraArgs['ServerSideEncryption'] = 'AES256'

    extraArgs['ContentType'] = mime_type

    return extraArgs


class S3Storage(StorageAbstract):
    """
    Implements a simple class to store files on AWS S3
    Can optionally set the outputs to be publically readable
    and can also encrypt files at rest
    """
    def __init__(self, bucket, prefix, public_access, encrypt, region):
        self.bucket = bucket
        self.public = public_access
        self.encrypt = encrypt
        self.prefix = prefix
        self.region = region

    def _wait_for(self, filename):
        import boto3
        client = boto3.client('s3', region_name=self.region)
        waiter = client.get_waiter('object_exists')
        waiter.wait(Bucket=self.bucket, Key=filename)

    def uploadData(self, data, filename, extraArgs):
        """
        :param data: Data to upload to S3
        :param filename: name of the file to upload to s3
                         will be appened to the configured prefix
        :returns: url to access the uploaded file
        Creates or updates a file on S3 in the bucket specified in the server
        configuration. The key of the created object will be equal to the
        configured prefix with the destination parameter appended.
        """
        import boto3

        s3 = boto3.resource('s3', region_name=self.region)
        s3.Object(self.bucket, filename).put(Body=data, **extraArgs)
        LOGGER.debug('S3 Put: {} into bucket {}'.format(self.bucket, filename))
        # Ensure object is available before returning URL
        self._wait_for(filename)

        # Create s3 URL
        url = self.url(filename)
        return url

    def uploadFileToS3(self, filename, extraArgs):
        """
        :param filename: Path to file on local filesystem
        :returns: url to access the uploaded file
        Uploads a file from the local filesystem to AWS S3
        """
        url = ''
        with open(filename, "rb") as data:
            s3_path = _build_s3_file_path(self.prefix, os.path.basename(filename))
            url = self.uploadData(data, s3_path, extraArgs)
        return url

    def store(self, output):
        """
        :param output: Of type IOHandler
        :returns: tuple(STORE_TYPE.S3, uploaded filename, url to access the uploaded file)
        Stores an IOHandler object to AWS S3 and returns the storage type, string and a URL
        to access the uploaded object
        """
        filename = output.file
        s3_path = _build_s3_file_path(self.prefix, os.path.basename(filename))
        extraArgs = _build_extra_args(
            public=self.public,
            encrypt=self.encrypt,
            mime_type=output.data_format.mime_type)
        url = self.uploadFileToS3(filename, extraArgs)
        return (STORE_TYPE.S3, s3_path, url)

    def write(self, data, destination, data_format=None):
        """
        :param data: Data that will be written to S3. Can be binary or text
        :param destination: Filename of object that will be created / updated
                            on S3.
        :param data_format: Format of the data. Will set the mime_type
                            of the file on S3. If not set, no mime_type will
                            be set.
        Creates or updates a file on S3 in the bucket specified in the server
        configuration. The key of the created object will be equal to the
        configured prefix with the destination parameter appended.
        """
        # Get MimeType from format if it exists
        mime_type = data_format.mime_type if data_format is not None else ''
        s3_path = _build_s3_file_path(self.prefix, destination)
        extraArgs = _build_extra_args(
            public=self.public,
            encrypt=self.encrypt,
            mime_type=mime_type)
        return self.uploadData(data, s3_path, extraArgs)

    def url(self, destination):
        """
        :param destination: File of object to create a URL for. This should
                            not include any prefix configured in the server
                            configuration.
        :returns: URL for accessing an object in S3 using a HTTPS GET
                  request
        """
        import boto3
        client = boto3.client('s3', region_name=self.region)
        url = '{}/{}/{}'.format(client.meta.endpoint_url, self.bucket, destination)
        LOGGER.debug('S3 URL calculated as: {}'.format(url))
        return url

    def location(self, destination):
        """
        :param destination: File of object to create a location for. This should
                            not include any prefix configured in the server
                            configuration.
        :returns: URL for accessing an object in S3 using a HTTPS GET
                  request
        """
        return self.url(destination)
