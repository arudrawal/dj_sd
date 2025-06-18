import boto3
import os
from botocore.exceptions import ClientError
from typing import Optional, Union
import logging

logger = logging.getLogger(__name__)


def get_s3_client():
    """Create and return an S3 client using AWS credentials."""
    return boto3.client('s3')


def download_s3_object(bucket_name: str, object_key: str, local_file_path: Optional[str] = None) -> Union[bytes, str]:
    """
    Download an object from S3 bucket.
    
    Args:
        bucket_name: Name of the S3 bucket
        object_key: Key/path of the object in S3
        local_file_path: Optional local file path to save the object
        
    Returns:
        If local_file_path is provided, returns the file path.
        Otherwise, returns the object content as bytes.
        
    Raises:
        ClientError: If there's an error accessing S3
    """
    s3_client = get_s3_client()
    
    try:
        if local_file_path:
            s3_client.download_file(bucket_name, object_key, local_file_path)
            logger.info(f"Downloaded {object_key} to {local_file_path}")
            return local_file_path
        else:
            response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
            content = response['Body'].read().decode('utf-8')
            logger.info(f"Retrieved {object_key} from {bucket_name}")
            return content
            
    except ClientError as e:
        logger.error(f"Error downloading {object_key} from {bucket_name}: {e}")
        raise


def get_s3_object_metadata(bucket_name: str, object_key: str) -> dict:
    """
    Get metadata for an S3 object.
    
    Args:
        bucket_name: Name of the S3 bucket
        object_key: Key/path of the object in S3
        
    Returns:
        Dictionary containing object metadata
        
    Raises:
        ClientError: If there's an error accessing S3
    """
    s3_client = get_s3_client()
    
    try:
        response = s3_client.head_object(Bucket=bucket_name, Key=object_key)
        return {
            'size': response.get('ContentLength'),
            'last_modified': response.get('LastModified'),
            'content_type': response.get('ContentType'),
            'etag': response.get('ETag'),
            'metadata': response.get('Metadata', {})
        }
    except ClientError as e:
        logger.error(f"Error getting metadata for {object_key} from {bucket_name}: {e}")
        raise


def list_s3_objects(bucket_name: str, prefix: str = "") -> list:
    """
    List objects in an S3 bucket with optional prefix filter.
    
    Args:
        bucket_name: Name of the S3 bucket
        prefix: Optional prefix to filter objects
        
    Returns:
        List of object keys
        
    Raises:
        ClientError: If there's an error accessing S3
    """
    s3_client = get_s3_client()
    
    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        if 'Contents' in response:
            return [obj['Key'] for obj in response['Contents']]
        return []
    except ClientError as e:
        logger.error(f"Error listing objects in {bucket_name}: {e}")
        raise