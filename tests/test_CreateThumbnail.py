import boto3
from unittest.mock import  Mock, patch

from CreateThumbnail.index import lambda_handler

class MockBotoClient:
    def get_object(self):
        return {}
    def put_object(self):
        return {
          'Expiration': 'string',
          'ETag': 'string',
          'VersionId': 'string',
          'SSECustomerAlgorithm': 'string',
          'SSECustomerKeyMD5': 'string',
          'SSEKMSKeyId': 'string',
          'SSEKMSEncryptionContext': 'string',
          'BucketKeyEnabled': False,
          'RequestCharged': 'requester'
          }

atrs = {'put_object.return_value': {}, 'get_object.return_value': {'Body': 'sadas'}}
@patch('CreateThumbnail.index.resize_image')
@patch.object(boto3, 'client')
def test_lambda_handler(
  mock_boto: Mock,
  mock_resize: Mock,
  s3_trigger_event: dict,
  mock_s3_get,
  mock_s3_put
):
    attrs = {
      'put_object.return_value': mock_s3_put,
      'get_object.return_value': mock_s3_get
    }
    mock_boto.return_value = Mock(**attrs)
    mock_resize.return_value = ""

    put_response = lambda_handler(s3_trigger_event, None)
    assert put_response == {
      'Expiration': 'string',
      'ETag': 'string',
      'VersionId': 'string',
      'SSECustomerAlgorithm': 'string',
      'SSECustomerKeyMD5': 'string',
      'SSEKMSKeyId': 'string',
      'SSEKMSEncryptionContext': 'string',
      'BucketKeyEnabled': False,
      'RequestCharged': 'requester'
    }