.. currentmodule:: pywps

.. _storage:

Storage
#######

.. todo::
    * Local file storage

In PyWPS, storage covers the storage of both the results that we want to return to the user and the storage of the execution status of each process.

AWS S3
-------

Amazon Web Services Simple Storage Service (AWS S3) can be used to store both process execution status XML documents and process result files. By using S3 we can allow easy public read access to process status and results on S3 using a variety of tools including the web browser, the AWS SDK and the AWS CLI.

For more information about AWS S3 please see https://aws.amazon.com/s3/ and for information about working with an S3 bucket see https://docs.aws.amazon.com/AmazonS3/latest/dev/UsingBucket.html

Requirements
=============

In order to work with S3 storage, you must first create an S3 bucket. https://docs.aws.amazon.com/AmazonS3/latest/dev/UsingBucket.html#create-bucket-intro

PyWPS uses the boto3 library to send requests to AWS. In order to make requests boto3 requires credentials which grant read and write access to the S3 bucket. Please see the boto3 guide on credentials for options on how to configure the credentials for your application. https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html

An example of an IAM policy that will allow PyWPS to read and write to the S3 Bucket is described here: https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_examples_s3_rw-bucket.html

``{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "ListObjectsInBucket",
            "Effect": "Allow",
            "Action": ["s3:ListBucket"],
            "Resource": ["arn:aws:s3:::bucket-name"]
        },
        {
            "Sid": "AllObjectActions",
            "Effect": "Allow",
            "Action": "s3:*Object",
            "Resource": ["arn:aws:s3:::bucket-name/*"]
        }
    ]
}``
