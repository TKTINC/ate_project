"""
ATE Storage Service - Storage Backend Utilities
Abstraction layer for different storage backends (local, S3, MinIO)
"""

import os
import boto3
from minio import Minio
from minio.error import S3Error
import tempfile
import shutil

class StorageBackend:
    """Abstraction layer for different storage backends"""
    
    def __init__(self, config):
        self.storage_type = config.get('STORAGE_TYPE', 'local')
        self.config = config
        
        if self.storage_type == 's3':
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=config.get('STORAGE_ACCESS_KEY'),
                aws_secret_access_key=config.get('STORAGE_SECRET_KEY'),
                region_name=config.get('AWS_REGION', 'us-east-1')
            )
            self.bucket = config.get('STORAGE_BUCKET')
            
        elif self.storage_type == 'minio':
            self.minio_client = Minio(
                config.get('STORAGE_ENDPOINT'),
                access_key=config.get('STORAGE_ACCESS_KEY'),
                secret_key=config.get('STORAGE_SECRET_KEY'),
                secure=config.get('STORAGE_SECURE', True)
            )
            self.bucket = config.get('STORAGE_BUCKET')
            
        elif self.storage_type == 'local':
            self.local_path = config.get('LOCAL_STORAGE_PATH', '/tmp/ate-storage')
            os.makedirs(self.local_path, exist_ok=True)
    
    def upload_file(self, storage_key, data):
        """Upload file data to storage backend"""
        if self.storage_type == 'local':
            return self._upload_local(storage_key, data)
        elif self.storage_type == 's3':
            return self._upload_s3(storage_key, data)
        elif self.storage_type == 'minio':
            return self._upload_minio(storage_key, data)
        else:
            raise ValueError(f"Unsupported storage type: {self.storage_type}")
    
    def download_file(self, storage_key):
        """Download file data from storage backend"""
        if self.storage_type == 'local':
            return self._download_local(storage_key)
        elif self.storage_type == 's3':
            return self._download_s3(storage_key)
        elif self.storage_type == 'minio':
            return self._download_minio(storage_key)
        else:
            raise ValueError(f"Unsupported storage type: {self.storage_type}")
    
    def delete_file(self, storage_key):
        """Delete file from storage backend"""
        if self.storage_type == 'local':
            return self._delete_local(storage_key)
        elif self.storage_type == 's3':
            return self._delete_s3(storage_key)
        elif self.storage_type == 'minio':
            return self._delete_minio(storage_key)
        else:
            raise ValueError(f"Unsupported storage type: {self.storage_type}")
    
    def file_exists(self, storage_key):
        """Check if file exists in storage backend"""
        if self.storage_type == 'local':
            return self._exists_local(storage_key)
        elif self.storage_type == 's3':
            return self._exists_s3(storage_key)
        elif self.storage_type == 'minio':
            return self._exists_minio(storage_key)
        else:
            raise ValueError(f"Unsupported storage type: {self.storage_type}")
    
    def get_file_info(self, storage_key):
        """Get file metadata from storage backend"""
        if self.storage_type == 'local':
            return self._info_local(storage_key)
        elif self.storage_type == 's3':
            return self._info_s3(storage_key)
        elif self.storage_type == 'minio':
            return self._info_minio(storage_key)
        else:
            raise ValueError(f"Unsupported storage type: {self.storage_type}")
    
    # Local storage implementation
    def _upload_local(self, storage_key, data):
        file_path = os.path.join(self.local_path, storage_key)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'wb') as f:
            if isinstance(data, str):
                f.write(data.encode())
            else:
                f.write(data)
        
        return {'storage_key': storage_key, 'size': len(data)}
    
    def _download_local(self, storage_key):
        file_path = os.path.join(self.local_path, storage_key)
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {storage_key}")
        
        with open(file_path, 'rb') as f:
            return f.read()
    
    def _delete_local(self, storage_key):
        file_path = os.path.join(self.local_path, storage_key)
        
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    
    def _exists_local(self, storage_key):
        file_path = os.path.join(self.local_path, storage_key)
        return os.path.exists(file_path)
    
    def _info_local(self, storage_key):
        file_path = os.path.join(self.local_path, storage_key)
        
        if not os.path.exists(file_path):
            return None
        
        stat = os.stat(file_path)
        return {
            'size': stat.st_size,
            'modified': stat.st_mtime,
            'storage_key': storage_key
        }
    
    # S3 storage implementation
    def _upload_s3(self, storage_key, data):
        if isinstance(data, str):
            data = data.encode()
        
        self.s3_client.put_object(
            Bucket=self.bucket,
            Key=storage_key,
            Body=data
        )
        
        return {'storage_key': storage_key, 'size': len(data)}
    
    def _download_s3(self, storage_key):
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket,
                Key=storage_key
            )
            return response['Body'].read()
        except self.s3_client.exceptions.NoSuchKey:
            raise FileNotFoundError(f"File not found: {storage_key}")
    
    def _delete_s3(self, storage_key):
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket,
                Key=storage_key
            )
            return True
        except Exception:
            return False
    
    def _exists_s3(self, storage_key):
        try:
            self.s3_client.head_object(
                Bucket=self.bucket,
                Key=storage_key
            )
            return True
        except self.s3_client.exceptions.NoSuchKey:
            return False
    
    def _info_s3(self, storage_key):
        try:
            response = self.s3_client.head_object(
                Bucket=self.bucket,
                Key=storage_key
            )
            return {
                'size': response['ContentLength'],
                'modified': response['LastModified'].timestamp(),
                'storage_key': storage_key,
                'etag': response['ETag']
            }
        except self.s3_client.exceptions.NoSuchKey:
            return None
    
    # MinIO storage implementation
    def _upload_minio(self, storage_key, data):
        if isinstance(data, str):
            data = data.encode()
        
        # Create a temporary file for MinIO upload
        with tempfile.NamedTemporaryFile() as temp_file:
            temp_file.write(data)
            temp_file.flush()
            
            self.minio_client.fput_object(
                self.bucket,
                storage_key,
                temp_file.name
            )
        
        return {'storage_key': storage_key, 'size': len(data)}
    
    def _download_minio(self, storage_key):
        try:
            with tempfile.NamedTemporaryFile() as temp_file:
                self.minio_client.fget_object(
                    self.bucket,
                    storage_key,
                    temp_file.name
                )
                
                with open(temp_file.name, 'rb') as f:
                    return f.read()
        except S3Error as e:
            if e.code == 'NoSuchKey':
                raise FileNotFoundError(f"File not found: {storage_key}")
            raise
    
    def _delete_minio(self, storage_key):
        try:
            self.minio_client.remove_object(self.bucket, storage_key)
            return True
        except Exception:
            return False
    
    def _exists_minio(self, storage_key):
        try:
            self.minio_client.stat_object(self.bucket, storage_key)
            return True
        except S3Error as e:
            if e.code == 'NoSuchKey':
                return False
            raise
    
    def _info_minio(self, storage_key):
        try:
            stat = self.minio_client.stat_object(self.bucket, storage_key)
            return {
                'size': stat.size,
                'modified': stat.last_modified.timestamp(),
                'storage_key': storage_key,
                'etag': stat.etag
            }
        except S3Error as e:
            if e.code == 'NoSuchKey':
                return None
            raise

