import boto3
import re
import os

from io import BytesIO
from PIL import Image
from typing import List, Optional


s3 = None
if os.environ.get('ENV') != "TEST":
    s3 = boto3.client('s3')

def get_source_and_dest_info(s3_object: dict) -> List[str]:
    source_bucket: str = s3_object['bucket']['name']

    # Object key may have spaces or unicode non-ASCII characters.
    src_key: str   = s3_object['object']['key']
    src_key = re.sub(r'/\+/g', ' ', src_key)
    dst_key: str  = f'resized-{src_key}'

    return [source_bucket, src_key, dst_key]

def resize_image(image_body: bytes, image_type):
    # set thumbnail width. Resize will set the height automatically to maintain aspect ratio.
    size  = (200,200)
    # size_split = size.split('x')
    try:
        img = Image.open(BytesIO(image_body))
        # size = img.size
        img = img.resize(size, Image.ANTIALIAS)

        mybuffer = BytesIO()
        img.save(mybuffer, format=image_type.upper())
        mybuffer.seek(0)
        return mybuffer
    except Exception as e:
        print(f'raise an exception of type {type(e)} while resizing image')
        raise e

def lambda_handler(event, context):
    print(os.listdir('/opt'))
    # Read options from the event parameter.
    print(f'EVENT:\n', event)

    # This is not production code, this is a hack to make this example's tests work
    global s3
    if not s3:
      s3 = boto3.client('s3')

    src_bckt, src_key, dst_key = get_source_and_dest_info(event['Records'][0]['s3'])
    dst_bucket: Optional[str] = os.environ.get('DestinationBucket')

    # Infer the image type from the file suffix.
    typeMatch: Optional[re.Match] = re.search(r'\.([^.]*)$', src_key)
    if not typeMatch:
        raise Exception('Could not determine the image type.')

    # Check that the image type is supported
    imageType: str = typeMatch[1].lower()
    if imageType not in ['jpg', 'jpeg', 'png']:
        raise Exception(f'Unsupported image type: {imageType}')

    # Download the image from the S3 source bucket.
    params = {
      'Bucket': src_bckt,
      'Key': src_key
    }
    origimage: dict = s3.get_object(**params)
    image_body: Optional[bytes] = origimage.get('Body').read()

    if not image_body:
        raise Exception('Something went wrong, image does not exist')

    resized = resize_image(image_body, imageType)

    # Upload the thumbnail image to the destination bucket
    destparams = {
      'Bucket': dst_bucket,
      'Key': dst_key,
      'Body': resized,
      'ContentType': 'image'
    }

    putResult: dict = s3.put_object(**destparams)

    print(
      f'Successfully resized {src_bckt}/{src_key} '
      f'and uploaded to {dst_bucket}/{dst_key}'
    )

    return putResult