"""
ATE Storage Service - Encryption Management Utilities
Secure encryption and decryption for tenant data
"""

import os
import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import secrets

class EncryptionManager:
    """Manages encryption and decryption operations for tenant data"""
    
    def __init__(self, master_key):
        self.master_key = master_key.encode() if isinstance(master_key, str) else master_key
        self.key_cache = {}
    
    def create_project_key(self, tenant_id, project_id):
        """Create a new encryption key for a project"""
        # Generate random salt
        salt = secrets.token_bytes(32)
        
        # Derive project-specific key from master key + tenant + project info
        key_material = f"{tenant_id}:{project_id}".encode()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        project_key = base64.urlsafe_b64encode(kdf.derive(self.master_key + key_material))
        
        # Encrypt the project key with master key for storage
        master_fernet = Fernet(base64.urlsafe_b64encode(self.master_key[:32]))
        encrypted_key = master_fernet.encrypt(project_key)
        
        return {
            'encrypted_key': base64.b64encode(encrypted_key).decode(),
            'salt': base64.b64encode(salt).decode(),
            'key_id': f"tenant-{tenant_id}-project-{project_id}"
        }
    
    def get_project_key(self, key_id, encrypted_key_data, salt):
        """Retrieve and decrypt project key"""
        if key_id in self.key_cache:
            return self.key_cache[key_id]
        
        # Decrypt the project key
        master_fernet = Fernet(base64.urlsafe_b64encode(self.master_key[:32]))
        encrypted_key = base64.b64decode(encrypted_key_data.encode())
        project_key = master_fernet.decrypt(encrypted_key)
        
        # Cache the key for performance
        self.key_cache[key_id] = project_key
        return project_key
    
    def encrypt_data(self, data, key_id):
        """Encrypt data using project-specific key"""
        # For this implementation, we'll use a simplified approach
        # In production, you'd retrieve the actual key from the database
        
        # Generate a simple key based on key_id for demo purposes
        key_hash = hashlib.sha256(f"{self.master_key.decode()}:{key_id}".encode()).digest()
        fernet_key = base64.urlsafe_b64encode(key_hash[:32])
        fernet = Fernet(fernet_key)
        
        if isinstance(data, str):
            data = data.encode()
        
        return fernet.encrypt(data)
    
    def decrypt_data(self, encrypted_data, key_id):
        """Decrypt data using project-specific key"""
        # Generate the same key based on key_id
        key_hash = hashlib.sha256(f"{self.master_key.decode()}:{key_id}".encode()).digest()
        fernet_key = base64.urlsafe_b64encode(key_hash[:32])
        fernet = Fernet(fernet_key)
        
        return fernet.decrypt(encrypted_data)
    
    def rotate_project_key(self, tenant_id, project_id, old_key_id):
        """Rotate encryption key for a project"""
        # Create new key
        new_key_data = self.create_project_key(tenant_id, project_id)
        
        # In a full implementation, you would:
        # 1. Re-encrypt all project data with the new key
        # 2. Update the database with the new key
        # 3. Securely delete the old key
        
        return new_key_data
    
    def generate_file_checksum(self, data):
        """Generate checksums for file integrity verification"""
        if isinstance(data, str):
            data = data.encode()
        
        md5_hash = hashlib.md5(data).hexdigest()
        sha256_hash = hashlib.sha256(data).hexdigest()
        
        return {
            'md5': md5_hash,
            'sha256': sha256_hash
        }
    
    def verify_file_integrity(self, data, expected_md5, expected_sha256):
        """Verify file integrity using checksums"""
        checksums = self.generate_file_checksum(data)
        
        md5_valid = checksums['md5'] == expected_md5
        sha256_valid = checksums['sha256'] == expected_sha256
        
        return {
            'valid': md5_valid and sha256_valid,
            'md5_valid': md5_valid,
            'sha256_valid': sha256_valid,
            'calculated_checksums': checksums
        }

